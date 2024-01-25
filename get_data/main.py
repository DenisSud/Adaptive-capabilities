import cv2
import os
import numpy as np
import csv
from datetime import datetime
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout
from bokeh.models.widgets import Button

# Global data dictionary for radius values
data = {'frame': [], 'radius': []}

# Create Bokeh figure
fig = figure(title="Radius Measurement", x_axis_label='Frame', y_axis_label='Radius', plot_height=400, plot_width=800)
source = ColumnDataSource(data=dict(x=[], y=[]))
line = fig.line('x', 'y', source=source)

# Create a button to quit
quit_button = Button(label="Quit", button_type="success")
quit_button.on_click(lambda: curdoc().clear())

# Set layout options
layout = layout([[fig], [quit_button]])

# Create a function to update the plot
def update_plot():
    global data
    source.data = dict(x=data['frame'], y=data['radius'])

# Function to measure radius
def measure_radius(frame):
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

# Function to create a unique CSV filename
def create_unique_csv_filename(directory, prefix):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_filename = f"{prefix}_{timestamp}_data.csv"
    full_path = os.path.join(directory, csv_filename)

    counter = 1
    while os.path.exists(full_path):
        csv_filename = f"{prefix}_{timestamp}_{counter}_data.csv"
        full_path = os.path.join(directory, csv_filename)
        counter += 1

    return full_path

# Function to process video frames
def process(csv_filename, camera_index=0):
    global data

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise ValueError("Error: Couldn't open the camera.")

    try:
        with open(csv_filename, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Frame', 'Radius'])

            frame_num = 1
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                radius = measure_radius(frame)
                print(f"Current Radius: {radius} pixels")
                data['frame'].append(frame_num)
                data['radius'].append(radius)

                writer.writerow([frame_num, radius])

                frame_num += 1

                update_plot()

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

    finally:
        cap.release()
        cv2.destroyAllWindows()

# Main execution
if __name__ == "__main__":
    csv_directory = "G:/Adaptive-capabilities/data/csv"
    csv_prefix = "data"

    csv_filename = create_unique_csv_filename(csv_directory, csv_prefix)
    print(f"Using CSV file: {csv_filename}")

    curdoc().add_root(layout)
    curdoc().title = "Radius Measurement"
    process(csv_filename)
