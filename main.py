import cv2
import numpy
import csv
import matplotlib.pyplot as plt
import signal
from matplotlib.widgets import Button


def measure_radius(frame: numpy.ndarray) -> tuple[float, numpy.ndarray]:
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
<<<<<<< HEAD
    _, thresholded_frame = cv2.threshold(gray_frame, 12, 255, cv2.THRESH_BINARY)    
=======
    _, thresholded_frame = cv2.threshold(gray_frame, 35, 255, cv2.THRESH_BINARY)    
>>>>>>> cd35e03bb5c90471d060598d5543b119b7081ff3

    light_pixel_count = cv2.countNonZero(thresholded_frame)
    dark_pixel_count = num_pixels - light_pixel_count

    cv2.imshow("frame", frame)
    cv2.imshow("thresholded_frame", thresholded_frame)

    radius = round(dark_pixel_count / numpy.pi)  # in pixels
    return radius, thresholded_frame

    
def process(csv_filename, camera_index=0):
<<<<<<< HEAD
=======
    i = csv_filename.find(".")
    if i != -1:
        csv_filename = "data/csv/" + csv_filename[:i] + ".csv"
    else:
        csv_filename = "data/csv/" + csv_filename
>>>>>>> cd35e03bb5c90471d060598d5543b119b7081ff3

    def signal_handler(sig, frame):
        nonlocal stop_processing
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
<<<<<<< HEAD
    quit_button.on_clicked(on_quit_button_clicked) 
=======
    quit_button.on_clicked(on_quit_button_clicked)
>>>>>>> cd35e03bb5c90471d060598d5543b119b7081ff3

    plt.show()

    while not stop_processing:
        ret, frame = cap.read()

        if not ret:
            break

        radius, _ = measure_radius(frame)
        print(f"Current Radius: {radius} pixels")
        data[len(data)] = radius

        # Update data for all values
        line_all.set_xdata(range(1, len(data) + 1))
        line_all.set_ydata(list(data.values()))

        # Update data for the last 500 values
        last_500_data = list(data.values())[-500:]
        line_last_500.set_xdata(range(1, len(last_500_data) + 1))
        line_last_500.set_ydata(last_500_data)

        # Update plot appearance
        for ax in [ax_all, ax_last_500]:
            ax.relim()
            ax.autoscale_view()

        plt.draw()
        plt.pause(0.08)

    # Save data to CSV after the loop is done or interrupted
    print

<<<<<<< HEAD
    with open(csv_filename, 'w', newline='') as file:
=======
    with open(csv_filename + ".csv", 'w', newline='') as file:
>>>>>>> cd35e03bb5c90471d060598d5543b119b7081ff3
        writer = csv.writer(file)
        for key, value in data.items():
            writer.writerow([key, value])
        print(f"Saved! ({csv_filename})")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
<<<<<<< HEAD
    csv_filename = input("enter the csv file that will be used: ")
    if csv_filename[-4:] == ".csv":
        print(f"Using CSV file: {csv_filename}")
    else:
        csv_filename += ".csv"
        print(f"Using CSV file: {csv_filename}")

    process(csv_filename, camera_index=1)
    print("Done")
=======
    csv_filename = "test"#input("enter the csv file that will be used: ")
    print(f"Using CSV file: {csv_filename}")

    process(csv_filename)
    print("Done")
>>>>>>> cd35e03bb5c90471d060598d5543b119b7081ff3
