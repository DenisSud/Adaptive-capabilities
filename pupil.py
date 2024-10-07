"""
Algorithmic approach
---

"""

import cv2
import numpy as np
import time
import random

class TrackerParams:
    def __init__(self):
        # Pupil size constraints
        self.pupil_min_radius = 20.0  # Minimum expected pupil radius in pixels
        self.pupil_max_radius = 100.0  # Maximum expected pupil radius in pixels

        # Canny edge detection parameters
        self.canny_threshold1 = 0.0  # Lower threshold for the hysteresis procedure in Canny
        self.canny_threshold2 = 255.0  # Upper threshold for the hysteresis procedure in Canny

        # Starburst algorithm parameters
        self.starburst_points = 30  # Number of rays to cast in the starburst algorithm

        # RANSAC parameters
        self.ransac_iterations = 1000  # Number of iterations for RANSAC ellipse fitting
        self.ransac_inlier_threshold = 2.0  # Maximum distance for a point to be considered an inlier

        # Image preprocessing parameters
        self.gaussian_blur_kernel_size = (31, 31)  # Kernel size for Gaussian blur
        self.gaussian_blur_sigma = 0  # Sigma (standard deviation) for Gaussian blur

        # Thresholding parameters
        self.threshold_value = 75  # Threshold value for binary image creation
        self.threshold_max_value = 255  # Maximum value to use with threshold

        # Canny edge detection additional parameters
        self.canny_aperture_size = 5  # Aperture size for the Sobel operator in Canny

        # Ellipse drawing parameters
        self.ellipse_thickness = 2  # Thickness of the ellipse line when drawn
        self.ellipse_color = (0, 0, 255)  # Color of the ellipse (BGR format)

        # Preprocessing specific parameters
        self.preprocess_blur_kernel_size = (31, 31)  # Kernel size for blur in preprocessing
        self.preprocess_blur_sigma = 0  # Sigma for blur in preprocessing

        # Pupil region detection parameters
        self.pupil_threshold = 75  # Threshold for isolating the pupil region

        # Edge detection specific parameters
        self.edge_aperture_size = 5  # Aperture size for Canny edge detection

        # Starburst visualization parameters
        self.starburst_point_radius = 2  # Radius of points drawn for starburst visualization
        self.starburst_point_color = (0, 255, 0)  # Color of starburst points (BGR format)

        # Output visualization parameters
        self.output_ellipse_thickness = 2  # Thickness of the final ellipse drawn on output
        self.output_ellipse_color = (0, 0, 255)  # Color of the final ellipse (BGR format)

class EdgePoint:
    def __init__(self, point):
        self.point = point

class FindPupilEllipseOut:
    def __init__(self, ellipse, processing_time):
        self.ellipse = ellipse
        self.processing_time = processing_time

def preprocess_image(image, params, step=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"/content/step_{step}_grayscale.jpg", gray)
    blurred = cv2.GaussianBlur(gray, params.gaussian_blur_kernel_size, params.gaussian_blur_sigma)
    cv2.imwrite(f"/content/step_{step}_blurred.jpg", blurred)
    return blurred

def detect_pupil_region(gray, params, step=2):
    _, threshold = cv2.threshold(gray, params.threshold_value, params.threshold_max_value, cv2.THRESH_BINARY_INV)
    cv2.imwrite(f"/content/step_{step}_threshold.jpg", threshold)
    return threshold

def find_largest_contour(binary, step=3):
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(output, [largest_contour], -1, (0, 255, 0), 2)
        cv2.imwrite(f"/content/step_{step}_largest_contour.jpg", output)  # Save contour image
        return largest_contour
    return None

def detect_edges(gray, params, step=4):
    edges = cv2.Canny(gray, params.canny_threshold1, params.canny_threshold2, apertureSize=params.canny_aperture_size)
    cv2.imwrite(f"/content/step_{step}_edges.jpg", edges)
    return edges

def starburst_edge_detection(edges, roi, params, step=5):
    edge_points = []
    center = (roi[0] + roi[2] // 2, roi[1] + roi[3] // 2)
    output = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    for i in range(params.starburst_points):
        angle = 2 * np.pi * i / params.starburst_points
        r = params.pupil_min_radius
        while r < params.pupil_max_radius:
            x = int(center[0] + r * np.cos(angle))
            y = int(center[1] + r * np.sin(angle))

            if 0 <= x < edges.shape[1] and 0 <= y < edges.shape[0]:
                if edges[y, x] == 255:
                    edge_points.append(EdgePoint((x, y)))
                    cv2.circle(output, (x, y), params.starburst_point_radius, params.starburst_point_color, -1)
                    break
            r += 1

    cv2.imwrite(f"/content/step_{step}_starburst_points.jpg", output)
    return edge_points

def ransac_ellipse_fit(edge_points, params):
    best_ellipse = None
    best_inliers = []
    rng = random.Random()

    for _ in range(params.ransac_iterations):
        if len(edge_points) < 5:
            continue

        sample = rng.sample(edge_points, 5)
        sample_points = np.array([ep.point for ep in sample], dtype=np.float32)
        ellipse = cv2.fitEllipse(sample_points)

        inliers = [ep for ep in edge_points if is_inlier(ep.point, ellipse, params.ransac_inlier_threshold)]
        if len(inliers) > len(best_inliers):
            best_ellipse = ellipse
            best_inliers = inliers

    if best_ellipse:
        return best_ellipse, best_inliers
    else:
        return None, []

def is_inlier(point, ellipse, threshold):
    center, axes, angle = ellipse
    cos_angle = np.cos(np.radians(angle))
    sin_angle = np.sin(np.radians(angle))

    dx = point[0] - center[0]
    dy = point[1] - center[1]

    x = dx * cos_angle + dy * sin_angle
    y = -dx * sin_angle + dy * cos_angle

    a = axes[0] / 2
    b = axes[1] / 2

    return abs((x**2 / a**2) + (y**2 / b**2) - 1) < threshold

def find_pupil_ellipse(image, params):
    start_time = time.time()

    gray = preprocess_image(image, params, step=1)
    binary = detect_pupil_region(gray, params, step=2)
    pupil_contour = find_largest_contour(binary, step=3)

    if pupil_contour is not None:
        bounding_rect = cv2.boundingRect(pupil_contour)
        edges = detect_edges(gray, params, step=4)
        edge_points = starburst_edge_detection(edges, bounding_rect, params, step=5)
        ellipse, _inliers = ransac_ellipse_fit(edge_points, params)

        return FindPupilEllipseOut(ellipse, time.time() - start_time)
    else:
        return FindPupilEllipseOut(None, time.time() - start_time)

def main():
    print("Starting pupil detection")
    image = cv2.imread("/content/eye.jpg")
    if image is None or image.size == 0:
        print("Failed to read image file '/content/eye.jpg'")
        return

    print(f"Input image size: {image.shape}")

    params = TrackerParams()
    print(f"Using default tracker parameters: {params.__dict__}")

    result = find_pupil_ellipse(image, params)

    if result.ellipse is not None:
        output = image.copy()
        center, axes, angle = result.ellipse
        center = (int(center[0]), int(center[1]))
        axes = (int(axes[0] / 2), int(axes[1] / 2))

        cv2.ellipse(output, center, axes, angle, 0, 360, params.output_ellipse_color, params.output_ellipse_thickness)

        cv2.imwrite("/content/step_6_output.jpg", output)
        print(f"Pupil detected. Output saved as '/content/step_6_output.jpg'. Processing time: {result.processing_time:.2f} s")
    else:
        print("No pupil detected.")

if __name__ == "__main__":
    main()
