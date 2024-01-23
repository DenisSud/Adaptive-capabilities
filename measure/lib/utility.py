import cv2
import numpy as np
from datetime import datetime

def get_radius():
    """
    Get the radius based on the count of dark pixels in the current webcam frame.

    Returns:
        float: Calculated radius.
    """
    cap = cv2.VideoCapture(0)  # Open the webcam at index 0

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        # Capture a single frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame.")
            return

        if frame is None:
            print("Error: Frame is empty.")
            return

        height, width, _ = frame.shape
        num_pixels = height * width

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresholded_frame = cv2.threshold(gray_frame, 68, 255, cv2.THRESH_BINARY)

        light_pixel_count = cv2.countNonZero(thresholded_frame)
        dark_pixel_count = num_pixels - light_pixel_count

        radius = round(dark_pixel_count / np.pi, 2)  # in pixels
        print(radius)

        # Get current timestamp
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    finally:
        # Release the webcam
        cap.release()
        cv2.destroyAllWindows()