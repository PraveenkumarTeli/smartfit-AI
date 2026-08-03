\# SmartFit AI - Real-Time Workout Analysis System



A computer vision-based fitness tracker that uses live pose estimation to count 

exercise repetitions, calculate joint angles, and track workout metrics in real time 

through a web interface.



\## Features



\- \*\*Real-time pose detection\*\* using MediaPipe's Pose Landmarker (33 body landmarks)

\- \*\*Live joint angle calculation\*\* using vector math (atan2-based)

\- \*\*Automatic rep counting\*\* via a finite state machine (tracks up/down motion cycles)

\- \*\*Full-body skeleton overlay\*\* rendered live on the video feed

\- \*\*Web-based interface\*\* built with Flask, streaming live video via MJPEG

\- \*\*Workout history storage\*\* using MySQL

\- \*\*Simulated smartwatch integration\*\* — heart rate data generated with realistic 

&#x20; drift patterns (real hardware integration planned as a future enhancement)

\- \*\*Live-updating stats\*\* (reps, heart rate) via JavaScript fetch + Flask JSON API



\## Tech Stack



\- \*\*Backend:\*\* Python, Flask

\- \*\*Computer Vision:\*\* OpenCV, MediaPipe (Tasks API)

\- \*\*Database:\*\* MySQL

\- \*\*Frontend:\*\* HTML, CSS, JavaScript

\- \*\*Other:\*\* python-dotenv (secure credential management)



\## Screenshots



\*(Add 1-2 of your screenshots here — drag them into the GitHub file editor, 

or reference them like: `!\[Live Tracking](screenshot1.png)`)\*



\## How It Works



1\. Webcam frames are captured with OpenCV

2\. Each frame is processed by MediaPipe's Pose Landmarker to detect 33 body landmarks

3\. Shoulder, elbow, and wrist coordinates are extracted to calculate the elbow joint angle

4\. A state machine tracks the angle to detect complete rep cycles (extended → curled → extended)

5\. Results are overlaid on the video and streamed live to a browser via Flask

6\. Workout data can be saved to a MySQL database on demand



\## Setup \& Installation



1\. Clone the repository:

