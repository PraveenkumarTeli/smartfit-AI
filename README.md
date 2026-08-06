# SmartFit AI - Real-Time Workout Analysis System

A computer vision-based fitness tracker that uses live pose estimation to count 
exercise repetitions, calculate joint angles, and track workout metrics in real time 
through a web interface.

## Features

- **Real-time pose detection** using MediaPipe's Pose Landmarker (33 body landmarks)
- **Live joint angle calculation** using vector math (atan2-based)
- **Automatic rep counting** via a finite state machine (tracks up/down motion cycles)
- **Full-body skeleton overlay** rendered live on the video feed
- **Multi-exercise support** — bicep curls (both arms) and squats, with an exercise selector
- **Camera on/off toggle** for pausing the live feed
- **Web-based interface** built with Flask, streaming live video via MJPEG
- **Workout history storage** using MySQL, with a visual progress chart (Chart.js)
- **Simulated smartwatch integration** — heart rate data generated with realistic 
  drift patterns (real hardware integration planned as a future enhancement)
- **Live-updating stats** (reps, squats, heart rate) via JavaScript fetch + Flask JSON API

## Tech Stack

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, MediaPipe (Tasks API)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Other:** python-dotenv (secure credential management)

## Screenshots

### Live Tracker
![Live Tracker](screenshots/tracker.png)

### Workout History
![Workout History](screenshots/history.png)

## How It Works

1. Webcam frames are captured with OpenCV
2. Each frame is processed by MediaPipe's Pose Landmarker to detect 33 body landmarks
3. Depending on the selected exercise, relevant joint coordinates are extracted 
   (shoulder-elbow-wrist for arms, hip-knee-ankle for squats)
4. A state machine tracks the angle to detect complete rep cycles
5. Results are overlaid on the video and streamed live to a browser via Flask
6. Workout data can be saved to a MySQL database on demand, and viewed later 
   on the history page with a progress chart

## Setup & Installation

1. Clone the repository:

git clone https://github.com/PraveenkumarTeli/smartfit-AI.git
cd smartfit-AI

2. Install dependencies:

pip install flask opencv-python mediapipe mysql-connector-python python-dotenv

3. Set up MySQL:
   - Create a database named `smartfit_db`
   - Create a `workouts` table (see schema below)

4. Create a `.env` file in the project root with:

DB_PASSWORD=your_mysql_password

5. Run the app:

python app.py

6. Open `http://127.0.0.1:5000` in your browser

## Database Schema

```sql
CREATE TABLE workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exercise VARCHAR(50),
    reps INT,
    date DATE
);
```

## Current Limitations & Future Improvements

- Smartwatch data is simulated due to hardware availability — real API 
  integration (Google Fit/Fitbit) planned
- No user authentication yet — single-user local use currently
- Additional exercise types (push-ups, lunges) could be added using the 
  same angle-based detection pattern

## Author

Built as a hands-on learning project to gain practical experience in computer 
vision, machine learning fundamentals, and full-stack development.