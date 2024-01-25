#include <iostream>
#include <opencv2/opencv.hpp>
#include <fstream>
#include <vector>
#include <ctime>
#include <csignal>
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;

bool stopProcessing = false;

void signalHandler(int signum) {
    stopProcessing = true;
}

std::string createUniqueCsvFilename(const std::string& directory, const std::string& prefix) {
    std::time_t timestamp = std::time(nullptr);
    char buffer[80];
    std::strftime(buffer, sizeof(buffer), "%Y%m%d%H%M%S", std::localtime(&timestamp));

    std::string csvFilename = prefix + "_" + buffer + "_data.csv";
    std::string fullPath = directory + "/" + csvFilename;

    int counter = 1;
    while (std::ifstream(fullPath.c_str())) {
        csvFilename = prefix + "_" + buffer + "_" + std::to_string(counter) + "_data.csv";
        fullPath = directory + "/" + csvFilename;
        counter++;
    }

    return fullPath;
}

std::pair<double, cv::Mat> measureRadius(const cv::Mat& frame) {
    if (frame.empty()) {
        throw std::invalid_argument("Error: Frame is empty");
    }

    int height = frame.rows;
    int width = frame.cols;
    int numPixels = height * width;

    cv::Mat grayFrame;
    cv::cvtColor(frame, grayFrame, cv::COLOR_BGR2GRAY);

    cv::Mat thresholdedFrame;
    cv::threshold(grayFrame, thresholdedFrame, 68, 255, cv::THRESH_BINARY);

    int lightPixelCount = cv::countNonZero(thresholdedFrame);
    int darkPixelCount = numPixels - lightPixelCount;

    cv::imshow("frame", frame);
    cv::imshow("thresholded_frame", thresholdedFrame);

    double radius = round(static_cast<double>(darkPixelCount) / M_PI, 2);  // in pixels
    return {radius, thresholdedFrame};
}

void process(const std::string& csvFilename, int cameraIndex = 0) {
    stopProcessing = false;
    signal(SIGINT, signalHandler);

    cv::VideoCapture cap(cameraIndex);
    std::map<int, double> data;

    if (!cap.isOpened()) {
        throw std::runtime_error("Error: Couldn't open the camera.");
    }

    plt::ion();
    plt::subplot(2, 1, 1);
    plt::title("Radius Over Time (All Data)");
    plt::named_plot("Radius (All Data)", std::vector<int>(), std::vector<double>());
    plt::legend();

    plt::subplot(2, 1, 2);
    plt::title("Radius Over Time (Last 500 Data)");
    plt::named_plot("Radius (Last 500 Data)", std::vector<int>(), std::vector<double>());
    plt::legend();

    plt::pause(0.01);

    try {
        std::ofstream csvFile(csvFilename);
        csvFile << "Frame,Radius\n";

        int frameNum = 1;
        while (!stopProcessing) {
            cv::Mat frame;
            cap.read(frame);

            if (frame.empty()) {
                break;
            }

            auto [radius, _] = measureRadius(frame);
            std::cout << "Current Radius: " << radius << " pixels\n";
            data[frameNum++] = radius;

            plt::subplot(2, 1, 1);
            plt::clf();
            plt::named_plot("Radius (All Data)", std::vector<int>(data.begin(), data.end()), std::vector<double>(data.begin(), data.end()));

            plt::subplot(2, 1, 2);
            plt::clf();
            std::vector<double> last500Data(data.begin(), data.end());
            if (last500Data.size() > 500) {
                last500Data.erase(last500Data.begin(), last500Data.end() - 500);
            }
            plt::named_plot("Radius (Last 500 Data)", std::vector<int>(last500Data.begin(), last500Data.end()), last500Data);

            plt::pause(0.01);

            csvFile << frameNum << "," << radius << "\n";

            char key = cv::waitKey(1);
            if (key == 'q') {
                stopProcessing = true;
            }
        }

        std::cout << "Data saved to " << csvFilename << std::endl;

    } catch (...) {
        cap.release();
        cv::destroyAllWindows();
    }
}

int main() {
    std::string csvDirectory = "G:/Adaptive-capabilities/data/csv";
    std::string csvPrefix = "data";

    std::string csvFilename = createUniqueCsvFilename(csvDirectory, csvPrefix);
    std::cout << "Using CSV file: " << csvFilename << std::endl;

    process(csvFilename);
    std::cout << "Done" << std::endl;

    return 0;
}
