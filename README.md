## OpenCV Radius Measurement

This project uses OpenCV to measure the radius of an object based on the count of dark pixels in a video frame. The results are plotted over time using Matplotlib and saved to a CSV file.

### Prerequisites
- Docker installed on your system
- User account with necessary permissions to run Docker commands

### Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/denissud/adaptive-capabilities.git
   ```

2. Change to the project directory:
   ```bash
   cd adaptive-capabilities
   ```

3. Build the Docker image:
   ```bash
   docker build -t adaptive-capabilitie .
   ```

4. Run the Docker container:
   ```bash
   docker run -it --rm -v /dev/video0:/dev/video0 --privileged adaptive-capabilitie
   ```
   - `-it`: Runs the container in interactive mode.
   - `--rm`: Automatically removes the container when it exits.
   - `-v /dev/video0:/dev/video0`: Mounts the webcam device from the host to the container.
   - `--privileged`: Grants the container additional privileges to access the webcam device.

5. When prompted, enter the CSV file name that will be used to save the data.

The Docker container will run the Python script, access the webcam, measure the radius, and save the data to the specified CSV file. The script will also display the radius over time using Matplotlib.

### File Structure
```
.
├── Dockerfile
├── app.py
└── README.md
```

- `Dockerfile`: Contains the instructions to build the Docker image.
- `app.py`: Your Python script that uses OpenCV to measure the radius.
- `README.md`: This README file.

### Dependencies
- Python 3.8
- OpenCV
- NumPy
- Matplotlib

### License
This project is licensed under the [MIT License](LICENSE).

Feel free to customize the README file according to your specific project details and requirements.
