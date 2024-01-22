import cv2
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import signal


def dark_area(frame):
    """
    Calculate the count of dark pixels in a given frame.

    Args:
        frame (numpy.ndarray): Input image frame.

    Returns:
        int: Count of dark pixels.
    """
    if frame is None:
        raise ValueError("Error: Frame is empty")

    height, width, _ = frame.shape
    num_pixels = height * width

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(gray_frame, 68, 255, cv2.THRESH_BINARY)    

    light_pixel_count = cv2.countNonZero(thresholded_frame)
    dark_pixel_count = num_pixels - light_pixel_count

    return dark_pixel_count

def measure(frame):
    """
    Measure the radius based on the count of dark pixels.

    Args:
        frame (numpy.ndarray): Input image frame.

    Returns:
        float: Calculated radius.
    """
    dark_pixel_count = dark_area(frame)
    radius = round(dark_pixel_count / np.pi, 2)  # in pixels
    return radius

def create_unique_csv_filename(directory, prefix):
    """
    Create a unique CSV filename based on the current timestamp.

    Args:
        directory (str): Directory path where the CSV file should be stored.
        prefix (str): Prefix for the CSV file.

    Returns:
        str: Unique CSV filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_filename = f"{prefix}_{timestamp}_data.csv"
    full_path = os.path.join(directory, csv_filename)

    # Check if the file already exists
    counter = 1
    while os.path.exists(full_path):
        csv_filename = f"{prefix}_{timestamp}_{counter}_data.csv"
        full_path = os.path.join(directory, csv_filename)
        counter += 1

    return full_path

def process_live_compare(csv_filename, camera_index=0):
    """
    Process live video feed, measure radius, and save data to CSV.

    Args:
        csv_filename (str): Path to the CSV file to save data.
        camera_index (int): Index of the camera to use (default is 0 for the default camera).
    """
    def signal_handler(sig, frame):
        """
        Signal handler to handle interrupt signal (Ctrl+C).
        """
        nonlocal stop_processing
        stop_processing = True

    stop_processing = False
    signal.signal(signal.SIGINT, signal_handler)

    cap = cv2.VideoCapture(camera_index)
    data = {}

    if not cap.isOpened():
        raise ValueError("Error: Couldn't open the camera.")

    plt.ion()
    _, ax = plt.subplots()
    line_fast, = ax.plot([], [], label='Radius')
    ax.set_title('Radius Over Time')
    ax.legend()
    plt.show()

    try:
        with open(csv_filename, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Frame', 'Radius'])

            while not stop_processing:
                ret, frame = cap.read()

                if not ret:
                    break

                radius = measure(frame)
                print(f"Current Radius: {radius} pixels")
                data[len(data)] = radius

                line_fast.set_xdata(range(1, len(data) + 1))
                line_fast.set_ydata(list(data.values()))

                ax.relim()
                ax.autoscale_view()
                cv2.imshow("frame", frame)
                plt.draw()
                plt.pause(0.01)

            # Save data to CSV after the loop is done or interrupted
            for frame_num, radius in data.items():
                writer.writerow([frame_num, radius])

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    csv_directory = "data/csv"
    csv_prefix = "data"
    
    csv_filename = create_unique_csv_filename(csv_directory, csv_prefix)
    print(f"Using CSV file: {csv_filename}")

    # Continue with the rest of your code, passing csv_filename to process_live_compare
    process_live_compare(csv_filename)
    print("Done") 