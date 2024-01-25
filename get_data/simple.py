import cv2
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import signal
from matplotlib.widgets import Button


def measure(frame):
    """
    Measure the radius based on the count of dark pixels.

    Args:
        frame (numpy.ndarray): Input image frame.

    Returns:
        float: Calculated radius.
    """
    if frame is None:
        raise ValueError("Error: Frame is empty")

    height, width, _ = frame.shape
    num_pixels = height * width

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(gray_frame, 68, 255, cv2.THRESH_BINARY)    

    light_pixel_count = cv2.countNonZero(thresholded_frame)
    dark_pixel_count = num_pixels - light_pixel_count

    radius = round(dark_pixel_count / np.pi, 2)  # in pixels
    return radius


def process():
    cap = cv2.VideoCapture(0)  # Open the webcam at index 0

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Create a CSV file for storing radius data
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame.")
            break

        radius = measure(frame)
        print(radius)
        # Get current timestamp
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close CSV file
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    csv_directory = "data/csv"
    csv_prefix = "data"

    process()
    print("Done")
