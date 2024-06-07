use opencv::{
    core,
    highgui,
    imgproc,
    prelude::*,
    videoio,
};
use plotters::prelude::*;
use csv::Writer;
use std::sync::{Arc, Mutex};
use signal_hook::{iterator::Signals, SIGINT};
use std::thread;

fn measure_radius(frame: &Mat) -> Result<(f64, Mat), Box<dyn std::error::Error>> {
    let mut gray_frame = Mat::default();
    imgproc::cvtColor(&frame, &mut gray_frame, imgproc::COLOR_BGR2GRAY, 0)?;

    let mut thresholded_frame = Mat::default();
    imgproc::threshold(&gray_frame, &mut thresholded_frame, 23.0, 255.0, imgproc::THRESH_BINARY)?;

    let light_pixel_count = core::count_non_zero(&thresholded_frame)?;
    let num_pixels = frame.rows() * frame.cols();
    let dark_pixel_count = num_pixels - light_pixel_count;

    let radius = (dark_pixel_count as f64 / std::f64::consts::PI).sqrt();
    Ok((radius, thresholded_frame))
}

fn process(csv_filename: &str, camera_index: i32) -> Result<(), Box<dyn std::error::Error>> {
    let stop_processing = Arc::new(Mutex::new(false));
    let stop_processing_clone = Arc::clone(&stop_processing);
    let mut signals = Signals::new(&[SIGINT])?;
    
    thread::spawn(move || {
        for _ in &signals {
            let mut stop = stop_processing_clone.lock().unwrap();
            *stop = true;
            break;
        }
    });

    let mut cap = videoio::VideoCapture::new(camera_index, videoio::CAP_ANY)?;
    if !videoio::VideoCapture::is_opened(&cap)? {
        return Err("Error: Couldn't open the camera.".into());
    }

    let root_area = BitMapBackend::new("plot.png", (640, 480)).into_drawing_area();
    root_area.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root_area)
        .caption("Radius Over Time", ("sans-serif", 50).into_font())
        .build_cartesian_2d(0..1000, 0.0..300.0)?;

    chart.configure_mesh().draw()?;

    let mut data = vec![];

    while !*stop_processing.lock().unwrap() {
        let mut frame = Mat::default();
        if !cap.read(&mut frame)? {
            break;
        }

        let (radius, _thresholded_frame) = measure_radius(&frame)?;
        println!("Current Radius: {} pixels", radius);
        data.push(radius);

        chart.draw_series(LineSeries::new(
            data.iter().enumerate().map(|(x, y)| (x as i32, *y)),
            &RED,
        ))?;
    }

    let mut wtr = Writer::from_path(csv_filename)?;
    for (i, radius) in data.iter().enumerate() {
        wtr.write_record(&[i.to_string(), radius.to_string()])?;
    }
    wtr.flush()?;

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut csv_filename = String::new();
    println!("Enter the CSV file that will be used: ");
    std::io::stdin().read_line(&mut csv_filename)?;
    csv_filename = csv_filename.trim().to_string();

    if !csv_filename.ends_with(".csv") {
        csv_filename.push_str(".csv");
    }
    println!("Using CSV file: {}", csv_filename);

    process(&csv_filename, 0)?;
    println!("Program finished!");

    Ok(())
}

