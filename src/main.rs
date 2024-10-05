use opencv::{
    core::{Size2f, Mat, Point, Point2f, Scalar, Size, Vector},
    imgcodecs, imgproc,
    prelude::*,
};
use rand::seq::SliceRandom;
use std::time::Instant;

// Structures

/// Parameters for pupil tracking algorithm
#[derive(Debug, Clone)]
struct TrackerParams {
    pupil_min_radius: f64,
    pupil_max_radius: f64,
    canny_threshold1: f64,
    canny_threshold2: f64,
    starburst_points: i32,
    ransac_iterations: i32,
}

impl Default for TrackerParams {
    fn default() -> Self {
        TrackerParams {
            pupil_min_radius: 5.0,
            pupil_max_radius: 50.0,
            canny_threshold1: 30.0,
            canny_threshold2: 100.0,
            starburst_points: 20,
            ransac_iterations: 100,
        }
    }
}

/// Represents a point on the edge of the pupil
#[derive(Debug, Clone)]
struct EdgePoint {
    point: Point2f,
}

/// Output of the pupil detection algorithm
#[derive(Debug)]
struct FindPupilEllipseOut {
    ellipse: Option<(Point2f, Size2f, f32)>,
    processing_time: f64,
}

// Main algorithm

/// Finds the pupil ellipse in the given image
///
/// # Arguments
///
/// * `image` - Input image
/// * `params` - Parameters for the tracking algorithm
///
/// # Returns
///
/// * `Result<FindPupilEllipseOut>` - Detected ellipse and processing time, or an error
fn find_pupil_ellipse(image: &Mat, params: &TrackerParams) -> opencv::Result<FindPupilEllipseOut> {
    let start_time = Instant::now();

    let gray = preprocess_image(image)?;
    let binary = detect_pupil_region(&gray)?;
    let pupil_contour = find_largest_contour(&binary)?;

    if let Some(pupil_contour) = pupil_contour {
        let bounding_rect = imgproc::bounding_rect(&pupil_contour)?;
        let edges = detect_edges(&gray, params)?;
        let edge_points = starburst_edge_detection(&edges, &bounding_rect, params)?;
        let (ellipse, _inliers) = ransac_ellipse_fit(&edge_points, params)?;

        Ok(FindPupilEllipseOut {
            ellipse: Some(ellipse),
            processing_time: start_time.elapsed().as_secs_f64(),
        })
    } else {
        Ok(FindPupilEllipseOut {
            ellipse: None,
            processing_time: start_time.elapsed().as_secs_f64(),
        })
    }
}

// Helper functions

/// Preprocesses the input image
fn preprocess_image(image: &Mat) -> opencv::Result<Mat> {
    let mut gray = Mat::default();
    imgproc::cvt_color(image, &mut gray, imgproc::COLOR_BGR2GRAY, 0)?;
    let mut blurred = Mat::default();
    imgproc::gaussian_blur(&gray, &mut blurred, Size::new(5, 5), 0.0, 0.0, opencv::core::BORDER_DEFAULT)?;
    Ok(blurred)
}

/// Detects the pupil region using thresholding
fn detect_pupil_region(gray: &Mat) -> opencv::Result<Mat> {
    let mut threshold = Mat::default();
    imgproc::threshold(gray, &mut threshold, 0.0, 255.0, imgproc::THRESH_BINARY_INV | imgproc::THRESH_OTSU)?;
    let mut binary = Mat::default();
    threshold.convert_to(&mut binary, opencv::core::CV_8UC1, 1.0, 0.0)?;
    Ok(binary)
}

/// Finds the largest contour in the binary image
fn find_largest_contour(binary: &Mat) -> opencv::Result<Option<Vector<Point>>> {
    let mut contours = Vector::<Vector<Point>>::new();
    imgproc::find_contours(binary, &mut contours, imgproc::RETR_EXTERNAL, imgproc::CHAIN_APPROX_SIMPLE, Point::new(0, 0))?;
    Ok(contours.iter().max_by_key(|c| imgproc::contour_area(c, false).unwrap() as i32).map(|c| c.clone()))
}

/// Detects edges in the image using Canny edge detection
fn detect_edges(gray: &Mat, params: &TrackerParams) -> opencv::Result<Mat> {
    let mut edges = Mat::default();
    imgproc::canny(
        gray,
        &mut edges,
        params.canny_threshold1,
        params.canny_threshold2,
        3,
        false,
    )?;
    Ok(edges)
}

/// Performs starburst edge detection
fn starburst_edge_detection(edges: &Mat, roi: &opencv::core::Rect, params: &TrackerParams) -> opencv::Result<Vec<EdgePoint>> {
    let mut edge_points = Vec::new();
    let center = Point2f::new(
        (roi.x + roi.width / 2) as f32,
        (roi.y + roi.height / 2) as f32,
    );

    for i in 0..params.starburst_points {
        let angle = 2.0 * std::f32::consts::PI * (i as f32) / (params.starburst_points as f32);
        let mut r = params.pupil_min_radius as f32;
        while r < params.pupil_max_radius as f32 {
            let x = (center.x + r * angle.cos()) as i32;
            let y = (center.y + r * angle.sin()) as i32;

            if x >= 0 && x < edges.cols() && y >= 0 && y < edges.rows() {
                if *edges.at_2d::<u8>(y, x)? == 255 {
                    edge_points.push(EdgePoint {
                        point: Point2f::new(x as f32, y as f32),
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

/// Fits an ellipse to the edge points using RANSAC
fn ransac_ellipse_fit(
    edge_points: &[EdgePoint],
    params: &TrackerParams,
) -> opencv::Result<((Point2f, Size2f, f32), Vec<EdgePoint>)> {
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
        let sample_vector = Vector::<Point2f>::from(sample);
        if let Ok(ellipse) = imgproc::fit_ellipse(&sample_vector) {
            let inliers: Vec<EdgePoint> = edge_points
                .iter()
                .filter(|ep| is_inlier(&ep.point, &(ellipse.center, ellipse.size, ellipse.angle), 2.0))
                .cloned()
                .collect();

            if inliers.len() > best_inliers.len() {
                best_ellipse = Some(ellipse);
                best_inliers = inliers;
            }
        }
    }

    best_ellipse
        .map(|e| ((e.center, e.size, e.angle), best_inliers))
        .ok_or_else(|| opencv::Error::new(0, "Failed to fit ellipse".to_string()))
}

/// Checks if a point is an inlier for the given ellipse
fn is_inlier(point: &Point2f, ellipse: &(Point2f, Size2f, f32), threshold: f64) -> bool {
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
    println!("Starting pupil detection");
    let image = imgcodecs::imread("eye.jpg", imgcodecs::IMREAD_COLOR)?;
    if image.empty() {
        return Err(opencv::Error::new(0, "Failed to read image file 'eye.jpg'".to_string()));
    }
    println!("Input image size: {:?}", image.size()?);

    let params = TrackerParams::default();
    println!("Using default tracker parameters: {:?}", params);

    let result = find_pupil_ellipse(&image, &params)?;

    if let Some(ellipse) = result.ellipse {
        let mut output = image.clone();
        let (center, size, angle) = ellipse;
        imgproc::ellipse(
            &mut output,
            Point::new(center.x as i32, center.y as i32),
            Size::new(size.width as i32, size.height as i32),
            angle as f64,
            0.0,
            360.0,
            Scalar::new(0.0, 0.0, 255.0, 0.0),
            2,
            imgproc::LINE_AA,
            0
        )?;

        imgcodecs::imwrite("output.jpg", &output, &Vector::new())?;
        println!("Pupil detected. Output saved as 'output.jpg'");
        println!("Processing time: {:.2} ms", result.processing_time * 1000.0);
    } else {
        println!("No pupil detected.");
    }

    Ok(())
}
