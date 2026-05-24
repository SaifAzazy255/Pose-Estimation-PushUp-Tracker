# 🏋️‍♂️ Pose-Estimation-PushUp-Tracker

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange.svg)
![NumPy](https://img.shields.io/badge/NumPy-Math-yellow.svg)

## 📌 Overview
A real-time fitness tracker utilizing MediaPipe Pose Estimation and OpenCV to accurately count push-ups via biomechanical angle analysis. Instead of relying on a black-box Machine Learning classifier, this system utilizes pure biomechanical math and trigonometry to calculate the exact angle of the elbow joint in real-time.

## 🎥 Demo Output
*(Put your final Pushup_Demo_Output.mp4 as a GIF here)*
`![PushUp Demo](link_to_your_gif_here)`

## ⚙️ How It Works (The Logic)
The script isolates the right arm's landmarks:
* **Point 12:** Right Shoulder
* **Point 14:** Right Elbow
* **Point 16:** Right Wrist

Using the Arctangent mathematical function, the system calculates the inner angle of the elbow:

$$\theta = \arctan2(y_3 - y_2, x_3 - x_2) - \arctan2(y_1 - y_2, x_1 - x_2)$$

* **UP State:** Angle > 160°
* **DOWN State:** Angle < 90°
* A repetition is successfully counted only when transitioning from a strict DOWN state back to an UP state.

## 🚀 Key Engineering Features
* **High-Fidelity Video Export:** Processes raw 60 FPS `.MOV` files and exports a mathematically smoothed 30 FPS `.MP4` output using `cv2.VideoWriter`.
* **Dynamic UI Rendering:** Real-time on-screen telemetry including state logic, repetition counting, and custom-offset filled circular markers indicating the active tracking nodes.
* **Frame-level Precision:** Manual frame iteration bypassing standard codec reading errors for strict start/end cropping (e.g., stopping exactly at frame 550).
  
