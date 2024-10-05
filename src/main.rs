use opencv::{
    core::{Mat, Point, Point2f, Scalar, Vec3b},
    imgcodecs, imgproc,
    prelude::*,
};
use rand::Rng;
use std::time::Instant;

// Structures

#[derive(Debug, Clone)]
struct TrackerParams {
    // Add parameters as needed
    pupil_min_radius: f64,
    pupil_max_radius: f64,
    canny_threshold1: f64,
    canny_threshold2: f64,
    starburstPoints: i32,
    ransac_iterations: i32,
}

impl Default for TrackerParams {
    fn default() -> Self {
        TrackerParams {
            pupil_min_radius: 5.0,
            pupil_max_radius: 50.0,
            canny_threshold1: 30.0,
            canny_threshold2: 100.0,
            starburstPoints: 20,
            ransac_iterations: 100,
        }
    }
}

#[derive(Debug, Clone)]
struct EdgePoint {
    point: Point2f,
    edge_strength: f64,
}

#[derive(Debug)]
struct FindPupilEllipseOut {
    ellipse: Option<(Point2f, opencv::core::Size2f, f32)>,
    inliers: Vec<EdgePoint>,
    processing_time: f64,
}

// Main algorithm
fn find_pupil_ellipse(image: &Mat, params: &TrackerParams) -> opencv::Result<FindPupilEllipseOut> {
    let start_time = Instant::now();

    // Step 1: Preprocess image
    let mut gray = Mat::default();
    imgproc::cvt_color(image, &mut gray, imgproc::COLOR_BGR2GRAY, 0)?;
    let mut blurred = Mat::default();
    imgproc::gaussian_blur(&gray, &mut blurred, opencv::core::Size::new(5, 5), 0.0, 0.0, opencv::core::BORDER_DEFAULT)?;

    // Step 2: Pupil region detection
    let threshold = imgproc::threshold(&blurred, &mut Mat::default(), 0.0, 255.0, imgproc::THRESH_BINARY_INV | imgproc::THRESH_OTSU)?;
    let mut contours = opencv::types::VectorOfVectorOfPoint::new();
    imgproc::find_contours(&threshold.1, &mut contours, imgproc::RETR_EXTERNAL, imgproc::CHAIN_APPROX_SIMPLE, Point::new(0, 0))?;

    // Find the largest contour (assumed to be the pupil)
    let pupil_contour = contours.iter().max_by_key(|c| imgproc::contour_area(c, false).unwrap() as i32);

    if let Some(pupil_contour) = pupil_contour {
        let bounding_rect = imgproc::bounding_rect(&pupil_contour)?;

        // Step 3: Edge detection
        let mut edges = Mat::default();
        imgproc::canny(
            &blurred,
            &mut edges,
            params.canny_threshold1,
            params.canny_threshold2,
            3,
            false,
        )?;

        // Step 4: Starburst edge detection
        let edge_points = starburst_edge_detection(&edges, &bounding_rect, params)?;

        // Step 5: RANSAC ellipse fitting
        let (ellipse, inliers) = ransac_ellipse_fit(&edge_points, params)?;

        let processing_time = start_time.elapsed().as_secs_f64();

        Ok(FindPupilEllipseOut {
            ellipse: Some(ellipse),
            inliers,
            processing_time,
        })
    } else {
        Ok(FindPupilEllipseOut {
            ellipse: None,
            inliers: vec![],
            processing_time: start_time.elapsed().as_secs_f64(),
        })
    }
}

// Helper functions

fn starburst_edge_detection(edges: &Mat, roi: &opencv::core::Rect, params: &TrackerParams) -> opencv::Result<Vec<EdgePoint>> {
    let mut edge_points = Vec::new();
    let center = Point2f::new(
        (roi.x + roi.width / 2) as f32,
        (roi.y + roi.height / 2) as f32,
    );

    for i in 0..params.starburstPoints {
        let angle = 2.0 * std::f32::consts::PI * (i as f32) / (params.starburstPoints as f32);
        let mut r = params.pupil_min_radius as f32;
        while r < params.pupil_max_radius as f32 {
            let x = (center.x + r * angle.cos()) as i32;
            let y = (center.y + r * angle.sin()) as i32;

            if x >= 0 && x < edges.cols() && y >= 0 && y < edges.rows() {
                if *edges.at_2d::<u8>(y, x)? == 255 {
                    edge_points.push(EdgePoint {
                        point: Point2f::new(x as f32, y as f32),
                        edge_strength: 1.0, // Simplified edge strength
                    });
                    break;
                }
            } else {
                break;
            }
            r += 1.0;
        }
    }

    Ok(edge_points)
}

fn ransac_ellipse_fit(
    edge_points: &[EdgePoint],
    params: &TrackerParams,
) -> opencv::Result<((Point2f, opencv::core::Size2f, f32), Vec<EdgePoint>)> {
    let mut rng = rand::thread_rng();
    let mut best_ellipse = None;
    let mut best_inliers = Vec::new();

    for _ in 0..params.ransac_iterations {
        if edge_points.len() < 5 {
            continue;
        }

        let sample: Vec<Point2f> = edge_points
            .choose_multiple(&mut rng, 5)
            .map(|ep| ep.point)
            .collect();

        if let Ok(ellipse) = imgproc::fit_ellipse(&opencv::types::VectorOfPoint2f::from(sample)) {
            let inliers: Vec<EdgePoint> = edge_points
                .iter()
                .filter(|ep| is_inlier(&ep.point, &ellipse, 2.0))
                .cloned()
                .collect();

            if inliers.len() > best_inliers.len() {
                best_ellipse = Some(ellipse);
                best_inliers = inliers;
            }
        }
    }

    best_ellipse
        .map(|e| (e, best_inliers))
        .ok_or_else(|| opencv::Error::new(0, "Failed to fit ellipse".to_string()))
}

fn is_inlier(point: &Point2f, ellipse: &(Point2f, opencv::core::Size2f, f32), threshold: f64) -> bool {
    let (center, size, angle) = ellipse;
    let cos_angle = angle.to_radians().cos() as f64;
    let sin_angle = angle.to_radians().sin() as f64;

    let dx = (point.x - center.x) as f64;
    let dy = (point.y - center.y) as f64;

    let x = dx * cos_angle + dy * sin_angle;
    let y = -dx * sin_angle + dy * cos_angle;

    let a = size.width as f64 / 2.0;
    let b = size.height as f64 / 2.0;

    ((x * x) / (a * a) + (y * y) / (b * b) - 1.0).abs() < threshold
}

fn main() -> opencv::Result<()> {
    let image = imgcodecs::imread("eye.jpg", imgcodecs::IMREAD_COLOR)?;
    let params = TrackerParams::default();

    let result = find_pupil_ellipse(&image, &params)?;

    if let Some(ellipse) = result.ellipse {
        let mut output = image.clone();
        imgproc::ellipse(
            &mut output,
            ellipse,
            Scalar::new(0.0, 0.0, 255.0, 0.0), // Red color
            2,
            imgproc::LINE_AA,
            0,
        )?;

        imgcodecs::imwrite("output.jpg", &output, &opencv::core::Vector::new())?;
        println!("Pupil detected. Output saved as 'output.jpg'");
        println!("Processing time: {:.2} ms", result.processing_time * 1000.0);
    } else {
        println!("No pupil detected.");
    }

    Ok(())
}
