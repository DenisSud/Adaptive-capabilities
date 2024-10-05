# Pupil Detection Algorithm

## Overview

This project implements a pupil detection algorithm using computer vision techniques in Rust. It utilizes the OpenCV library to process images and detect the pupil, fitting an ellipse to represent its shape.

## Features

- Pupil detection in eye images
- Ellipse fitting to represent the pupil shape
- Starburst edge detection algorithm
- RANSAC-based ellipse fitting for robustness
- Performance timing

## Requirements

- Rust 1.70.0 or later
- OpenCV 4.5.0 or later
- Cargo (Rust's package manager)

## Dependencies

- opencv = "^0.93.0"
- rand = "^0.8.5"

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/pupil-detection.git
   cd pupil-detection
   ```

2. Build the project:
   ```
   cargo build --release
   ```

## Usage

1. Place an image file named `eye.jpg` in the project root directory.
2. Run the program:
   ```
   cargo run --release
   ```
3. The program will process the image and output the results, including:
   - Whether a pupil was detected
   - The processing time
   - An output image named `output.jpg` with the detected pupil ellipse drawn on it (if a pupil was found)

## Customization

You can modify the `TrackerParams` struct in the code to adjust various parameters of the algorithm, such as:

- Minimum and maximum pupil radius
- Canny edge detection thresholds
- Number of starburst points
- Number of RANSAC iterations

## Contributing

Contributions to improve the algorithm or extend its functionality are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a new Pull Request

## Future Improvements

- Implement multi-threading for faster processing
- Add support for video input
- Improve robustness for different lighting conditions
- Implement a graphical user interface

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV community for their excellent computer vision library
- Rust community for the powerful and safe programming language

## Contact

For any questions or suggestions, please open an issue in the GitHub repository.
