import cv2
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.widgets import Button
import threading
import queue

# Global queue for communication between threads
frame_queue = queue.Queue()

# Global data dictionary for radius values
data = {}

def measure_radius(frame):
    if frame is None:
        raise ValueError("Error: Frame is empty")

    height, width, _ = frame.shape
    num_pixels = height * width

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(gray_frame, 68, 255, cv2.THRESH_BINARY)    

    light_pixel_count = cv2.countNonZero(thresholded_frame)
    dark_pixel_count = num_pixels - light_pixel_count

    cv2.imshow("frame", frame)
    cv2.imshow("thresholded_frame", thresholded_frame)

    radius = round(dark_pixel_count / np.pi, 2)  # in pixels
    return radius, thresholded_frame

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

def open_cv_thread(camera_index):
    cap = cv2.VideoCapture(camera_index)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_queue.put(frame)
    finally:
        cap.release()

def cv2_mouse_callback(event, x, y, flags, param):
    # Handle mouse events for OpenCV windows
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse click at (x={x}, y={y})")

def matplotlib_thread():
    global data  # Use the global data dictionary
    plt.ion()
    _, (ax_all, ax_last_500) = plt.subplots(2, 1, figsize=(8, 8))
    line_all, = ax_all.plot([], [], label='Radius (All Data)')
    line_last_500, = ax_last_500.plot([], [], label='Radius (Last 500 Data)')

    ax_all.set_title('Radius Over Time (All Data)')
    ax_all.legend()

    ax_last_500.set_title('Radius Over Time (Last 500 Data)')
    ax_last_500.legend()

    quit_button_ax = plt.axes([0.8, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
    quit_button = Button(quit_button_ax, 'Quit')

    plt.show()

    while True:
        try:
            frame = frame_queue.get(timeout=0.1)
            radius, _ = measure_radius(frame)
            print(f"Current Radius: {radius} pixels")

            data[len(data)] = radius

            line_all.set_xdata(range(1, len(data) + 1))
            line_all.set_ydata(list(data.values()))

            last_500_data = list(data.values())[-500:]
            line_last_500.set_xdata(range(1, len(last_500_data) + 1))
            line_last_500.set_ydata(last_500_data)

            for ax in [ax_all, ax_last_500]:
                ax.relim()
                ax.autoscale_view()

            plt.draw()
            plt.pause(0.01)

            cv2.imshow("frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                plt.close('all')  # Close all Matplotlib windows on 'q' key press
                break

        except queue.Empty:
            pass

def process(csv_filename, camera_index=0):
    global data

    def signal_handler(sig, frame):
        nonlocal stop_processing
        stop_processing = True

    def key_handler(key):
        nonlocal stop_processing
        if key == ord('q'):
            stop_processing = True

    def on_quit_button_clicked(event):
        nonlocal stop_processing
        stop_processing = True

    stop_processing = False
    signal.signal(signal.SIGINT, signal_handler)

    cap = cv2.VideoCapture(camera_index)
    data = {}

    if not cap.isOpened():
        raise ValueError("Error: Couldn't open the camera.")

    plt.ion()
    _, (ax_all, ax_last_500) = plt.subplots(2, 1, figsize=(8, 8))
    line_all, = ax_all.plot([], [], label='Radius (All Data)')
    line_last_500, = ax_last_500.plot([], [], label='Radius (Last 500 Data)')

    ax_all.set_title('Radius Over Time (All Data)')
    ax_all.legend()

    ax_last_500.set_title('Radius Over Time (Last 500 Data)')
    ax_last_500.legend()

    quit_button_ax = plt.axes([0.8, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
    quit_button = Button(quit_button_ax, 'Quit')
    quit_button.on_clicked(on_quit_button_clicked)

    plt.show()

    try:
        with open(csv_filename, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Frame', 'Radius'])

            while not stop_processing:
                ret, frame = cap.read()

                if not ret:
                    break

                radius, _ = measure_radius(frame)
                print(f"Current Radius: {radius} pixels")
                data[len(data)] = radius

                line_all.set_xdata(range(1, len(data) + 1))
                line_all.set_ydata(list(data.values()))

                last_500_data = list(data.values())[-500:]
                line_last_500.set_xdata(range(1, len(last_500_data) + 1))
                line_last_500.set_ydata(last_500_data)

                for ax in [ax_all, ax_last_500]:
                    ax.relim()
                    ax.autoscale_view()

                plt.draw()
                plt.pause(0.01)

                key = cv2.waitKey(1) & 0xFF
                key_handler(key)

            for frame_num, radius in data.items():
                writer.writerow([frame_num, radius])
            print(f"Data saved to {csv_filename}")

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    csv_directory = "G:/Adaptive-capabilities/data/csv"
    csv_prefix = "data"
    
    csv_filename = create_unique_csv_filename(csv_directory, csv_prefix)
    print(f"Using CSV file: {csv_filename}")

    # Start the OpenCV thread
    opencv_thread = threading.Thread(target=open_cv_thread, args=(0,))
    opencv_thread.start()

    # Start the Matplotlib thread
    matplotlib_thread = threading.Thread(target=matplotlib_thread)
    matplotlib_thread.start()

    try:
        process(csv_filename)
    finally:
        opencv_thread.join()
        matplotlib_thread.join()

    print("Done")
