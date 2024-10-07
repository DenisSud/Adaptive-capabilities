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
    preprocess_blur_kernel_size: (i32, i32),  // Size of the Gaussian blur kernel for preprocessing
    preprocess_blur_sigma: f64,               // Standard deviation for Gaussian blur
    pupil_min_radius: f64,                    // Minimum expected pupil radius
    pupil_max_radius: f64,                    // Maximum expected pupil radius
    canny_threshold1: f64,                    // First threshold for Canny edge detection
    canny_threshold2: f64,                    // Second threshold for Canny edge detection
    starburst_points: i32,                    // Number of rays to use in starburst algorithm
    ransac_iterations: i32,                   // Number of iterations for RANSAC ellipse fitting
    threshold_value: f64,                     // Threshold value for binary image creation
    threshold_max_value: f64,                 // Maximum value to use with thresholding
    canny_aperture_size: i32,                 // Aperture size for Canny edge detection
    ransac_inlier_threshold: f64,             // Distance threshold for RANSAC inliers
    starburst_point_radius: i32,              // Radius of points drawn in starburst visualization
    starburst_point_color: Scalar,            // Color of points in starburst visualization
    output_ellipse_thickness: i32,            // Thickness of the final ellipse drawn
    output_ellipse_color: Scalar,             // Color of the final ellipse drawn
}
impl Default for TrackerParams {
    fn default() -> Self {
        TrackerParams {
            pupil_min_radius: 20.0,
            pupil_max_radius: 100.0,
            canny_threshold1: 0.0,
            canny_threshold2: 255.0,
            starburst_points: 1000,
            ransac_iterations: 1000,
            ransac_inlier_threshold: 2.0,
            threshold_value: 75.0,
            threshold_max_value: 255.0,
            canny_aperture_size: 5,
            preprocess_blur_kernel_size: (31, 31),
            preprocess_blur_sigma: 0.0,
            starburst_point_radius: 2,
            starburst_point_color: Scalar::new(0.0, 255.0, 0.0, 0.0),
            output_ellipse_thickness: 2,
            output_ellipse_color: Scalar::new(0.0, 0.0, 255.0, 0.0),
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

    let gray = preprocess_image(image, &params)?;
    let binary = detect_pupil_region(&gray, &params)?;
    let pupil_contour = find_largest_contour(&binary)?;

    if let Some(pupil_contour) = pupil_contour {
        let bounding_rect = imgproc::bounding_rect(&pupil_contour)?;
        let edges = detect_edges(&gray, params)?;
        let edge_points = starburst_edge_detection(&edges, &bounding_rect, params)?;
        let (ellipse, _inliers) = ransac_ellipse_fit(&edge_points, params)?;

        Ok(FindPupilEllipseOut {
            ellipse: ellipse,
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
fn preprocess_image(image: &Mat, params: &TrackerParams) -> opencv::Result<Mat> {
    let mut gray = Mat::default();
    imgproc::cvt_color(image, &mut gray, imgproc::COLOR_BGR2GRAY, 0)?;
    imgcodecs::imwrite("images/step_1_grayscale.jpg", &gray, &Vector::new())?;

    let mut blurred = Mat::default();
    imgproc::gaussian_blur(
        &gray,
        &mut blurred,
        Size::new(params.preprocess_blur_kernel_size.0, params.preprocess_blur_kernel_size.1),
        params.preprocess_blur_sigma,
        params.preprocess_blur_sigma,
        opencv::core::BORDER_DEFAULT
    )?;
    imgcodecs::imwrite("images/step_1_blurred.jpg", &blurred, &Vector::new())?;

    Ok(blurred)
}

/// Detects the pupil region using thresholding
fn detect_pupil_region(gray: &Mat, params: &TrackerParams) -> opencv::Result<Mat> {
    let mut threshold = Mat::default();
    imgproc::threshold(
        gray,
        &mut threshold,
        params.threshold_value,
        params.threshold_max_value,
        imgproc::THRESH_BINARY_INV
    )?;
    imgcodecs::imwrite("images/step_2_threshold.jpg", &threshold, &Vector::new())?;
    Ok(threshold)
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
        params.canny_aperture_size,
        false,
    )?;
    imgcodecs::imwrite("images/step_4_edges.jpg", &edges, &Vector::new())?;
    Ok(edges)
}

/// Performs starburst edge detection
fn starburst_edge_detection(gray: &Mat, roi: &opencv::core::Rect, params: &TrackerParams) -> opencv::Result<Vec<EdgePoint>> {
    let mut edges = Mat::default();
    imgproc::canny(
        gray,
        &mut edges,
        params.canny_threshold1,
        params.canny_threshold2,
        params.canny_aperture_size,
        false,
    )?;

    let mut edge_points = Vec::new();
    let center = Point2f::new((roi.x + roi.width / 2) as f32, (roi.y + roi.height / 2) as f32);

    let mut output = Mat::default();
    imgproc::cvt_color(&edges, &mut output, imgproc::COLOR_GRAY2BGR, 0)?;

    for i in 0..params.starburst_points {
        let angle = 2.0 * std::f32::consts::PI * (i as f32) / (params.starburst_points as f32);
        if let Some(edge_point) = find_edge_point(&edges, center, angle, params) {
            edge_points.push(edge_point.clone()); // Clone the EdgePoint before pushing
            draw_starburst_point(&mut output, edge_point.point, params)?;
        }
    }

    imgcodecs::imwrite("images/step_5_starburst_points.jpg", &output, &Vector::new())?;
    Ok(edge_points)
}

fn find_edge_point(edges: &Mat, center: Point2f, angle: f32, params: &TrackerParams) -> Option<EdgePoint> {
    let mut radius = params.pupil_min_radius as f32;
    while radius < params.pupil_max_radius as f32 {
        let x = (center.x + radius * angle.cos()) as i32;
        let y = (center.y + radius * angle.sin()) as i32;

        if x >= 0 && x < edges.cols() && y >= 0 && y < edges.rows() {
            if *edges.at_2d::<u8>(y, x).ok()? == 255 {
                return Some(EdgePoint { point: Point2f::new(x as f32, y as f32) });
            }
        }
        radius += 1.0;
    }
    None
}

fn draw_starburst_point(output: &mut Mat, point: Point2f, params: &TrackerParams) -> opencv::Result<()> {
    imgproc::circle(
        output,
        Point::new(point.x as i32, point.y as i32),
        params.starburst_point_radius,
        params.starburst_point_color,
        -1,
        imgproc::LINE_AA,
        0,
    )
}

/// Fits an ellipse to the edge points using RANSAC
fn ransac_ellipse_fit(
    edge_points: &[EdgePoint],
    params: &TrackerParams,
) -> opencv::Result<(Option<(Point2f, Size2f, f32)>, Vec<EdgePoint>)> {
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
                .filter(|ep| is_inlier(&ep.point, &(ellipse.center, ellipse.size, ellipse.angle), params.ransac_inlier_threshold))
                .cloned()
                .collect();

            if inliers.len() > best_inliers.len() {
                best_ellipse = Some((ellipse.center, ellipse.size, ellipse.angle));
                best_inliers = inliers;
            }
        }
    }

    Ok((best_ellipse, best_inliers))
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
    let image = imgcodecs::imread("images/eye.jpg", imgcodecs::IMREAD_COLOR)?;
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
            Size::new(size.width as i32 / 2, size.height as i32 / 2),
            angle as f64,
            0.0,
            360.0,
            params.output_ellipse_color,
            params.output_ellipse_thickness,
            imgproc::LINE_AA,
            0
        )?;

        imgcodecs::imwrite("images/step_6_output.jpg", &output, &Vector::new())?;
        println!("Pupil detected. Output saved as 'images/step_6_output.jpg'");
        println!("Processing time: {:.2} ms", result.processing_time * 1000.0);
    } else {
        println!("No pupil detected.");
    }

    Ok(())
}
