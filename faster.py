import signal
import cv2
import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def measure_radius(frame: np.ndarray) -> float:
  """
  Measure the radius based on the count of dark pixels.

  Args:
      frame (np.ndarray): Input image frame.

  Returns:
      float: Calculated radius.
  """
  if frame is None:
    raise ValueError("Error: Frame is empty")

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  _, thresholded_frame = cv2.threshold(gray, 16, 255, cv2.THRESH_BINARY)
  dark_pixel_count = np.count_nonzero(thresholded_frame == 0)  # Faster counting

  radius = round(dark_pixel_count / np.pi)  # in pixels
  return radius


def process(csv_filename, camera_index=0):

  def signal_handler(sig, frame):
    nonlocal stop_processing
    stop_processing = True

  def on_quit_button_clicked(event):
    nonlocal stop_processing
    stop_processing = True

  stop_processing = False
  signal.signal(signal.SIGINT, signal_handler)

  cap = cv2.VideoCapture(camera_index)
  data = []  # Use a list for faster storage

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

  frame_count = 0
  last_500_data = []

  while not stop_processing:
    ret, frame = cap.read()

    if not ret:
      break

    frame_count += 1

    # Process only every Nth frame (adjust N for desired speed vs accuracy)
    if frame_count % 5 != 0:
      continue

    radius = measure_radius(frame)
    data.append(radius)

    # Update data for all values (less frequent updates)
    if frame_count % 50 == 0:
      line_all.set_xdata(range(1, len(data) + 1))
      line_all.set_ydata(data)

    # Update data for last 500 values
    last_500_data.append(radius)
    if len(last_500_data) > 500:
      last_500_data.pop(0)  # Maintain a fixed size list

    line_last_500.set_xdata(range(1, len(last_500_data) + 1))
    line_last_500.set_ydata(last_500_data)

    # Update plot appearance (less frequent)
    if frame_count % 50 == 0:
      for ax in [ax_all, ax_last_500]:
        ax.relim()
        ax.autoscale_view()

    plt.draw()
    plt.pause(0.01)  # Reduce pause time

  # Save data to CSV after the loop is done or interrupted
  with open(csv_filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(enumerate)

if __name__ == "__main__":
    csv_filename = input("enter the csv file that will be used: ")
    if csv_filename[-4:] == ".csv":
        print(f"Using CSV file: {csv_filename}")
    else:
        csv_filename += ".csv"
        print(f"Using CSV file: {csv_filename}")

    process(csv_filename, camera_index=0)
    print("Done")