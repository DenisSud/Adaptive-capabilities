import cv2
import os
import numpy as np
import csv

def measure_radius(frame):
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
    _, thresholded_frame = cv2.threshold(gray_frame, 35, 255, cv2.THRESH_BINARY)    

    light_pixel_count = cv2.countNonZero(thresholded_frame)
    dark_pixel_count = num_pixels - light_pixel_count

    cv2.imshow("frame", frame)
    cv2.imshow("thresholded_frame", thresholded_frame)

    radius = round(dark_pixel_count / np.pi)  # in pixels
    return radius, frame

# Function to process a video and extract frames
def process_video(video_path, output_folder):
    cap, err = cv2.VideoCapture(video_path)
    if err 
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        radius, frame = measure_radius(frame)

        # Save the pair of input frame and radius in a CSV file
        csv_row = [os.path.basename(video_path), i, radius]
        csv_file_path = os.path.join(output_folder, 'training_data.csv')

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)

    cap.release()

# Example usage for one video
videos_folder = 'C:/Users/sudak/code/Adaptive-capabilities/data/video/'
output_folder = 'C:/Users/sudak/code/Adaptive-capabilities/data/csv/'

video_file = 'Алейникова Дарья 17.03.2023.mkv'  # Replace with the actual video file name
video_path = os.path.join(videos_folder, video_file)

process_video(video_path, output_folder)
