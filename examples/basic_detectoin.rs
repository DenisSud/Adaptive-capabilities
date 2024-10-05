use opencv::imgcodecs;
use pupil::pupil_detection::{find_pupil_ellipse, TrackerParams};

fn main() -> opencv::Result<()> {
    let image = imgcodecs::imread("eye.jpg", imgcodecs::IMREAD_COLOR)?;
    let params = TrackerParams::default();
    let result = find_pupil_ellipse(&image, &params)?;

    if let Some(ellipse) = result.ellipse {
        println!("Pupil detected: {:?}", ellipse);
        println!("Processing time: {} ms", result.processing_time * 1000.0);
    } else {
        println!("No pupil detected");
    }

    Ok(())
}
