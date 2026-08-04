from flask import Flask, Response,render_template,jsonify
import cv2
import mediapipe as mp
from angle_utils import calculate_angle
import mysql.connector
from smartwatch_api import get_heart_rate
import os
from dotenv import load_dotenv
load_dotenv()
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.environ.get("DB_PASSWORD"),
    database="smartfit_db"
)


app = Flask(__name__)

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='pose_landmarker_lite.task'),
    running_mode=VisionRunningMode.VIDEO
)
landmarker = PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
frame_timestamp_ms = 0
counter = 0
stage_right = "down"
stage_left = "down"
squat_counter = 0
stage_squat = "up"

connections = [
    (11, 12), (12, 14), (14, 16), (11, 13), (13, 15),
    (11, 23), (12, 24), (23, 24),
    (24, 26), (26, 28), (23, 25), (25, 27)
]

def generate_frames():
    global frame_timestamp_ms, counter, stage_right,stage_left,squat_counter,stage_squat

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        if result.pose_landmarks:
            h, w, _ = frame.shape
            for pose in result.pose_landmarks:
                shoulder_r, elbow_r, wrist_r = pose[12], pose[14], pose[16]
                angle_r = calculate_angle(shoulder_r, elbow_r, wrist_r)

                if angle_r < 50 and stage_right == "down":
                    stage_right  = "up"
                if angle_r > 160 and stage_right  == "up":
                    stage_right = "down"
                    counter = counter + 1
                shoulder_l,elbow_l,wrist_l= pose[11],pose[13],pose[15]
                angle_l= calculate_angle(shoulder_l,elbow_l,wrist_l)

                if angle_l <50 and stage_left == "down":
                    stage_left  = "up"
                if angle_l > 160 and stage_left == "up":
                    stage_left = "down"
                    counter = counter + 1

                hip,knee,ankle = pose[24],pose[26],pose[28]
                angle_knee=calculate_angle(hip,knee,ankle )
                if angle_knee < 90 and stage_squat == "up":
                    stage_squat = "down"
                if angle_knee > 160 and stage_squat == "down":
                    stage_squat = "up"
                    squat_counter = squat_counter + 1
                
                for start_idx, end_idx in connections:
                    start = pose[start_idx]
                    end = pose[end_idx]
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, start_point, end_point, (0, 0, 255), 2)

                for lm in pose:
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

                cv2.putText(frame, "R Angle: " + str(int(angle_r)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "L Angle: " + str(int(angle_l)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Rep Count: "+str(counter), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "knee Angle: " + str(int(angle_knee)), (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "squat count: "+str(squat_counter), (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "BPM: "+str(int(get_heart_rate())), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/save_workout')
def save_workout():
    cursor=conn.cursor()
    cursor.execute("INSERT INTO workouts (exercise,reps,date) VALUES(%s,%s,%s)",("bicep_curl",counter,"2028-08-02"))
    cursor.execute("INSERT INTO workouts (exercise,reps,date) VALUES(%s,%s,%s)",("squat",squat_counter,"2028-08-02"))
    conn.commit()
    return "workout saved!"
@app.route('/get_stats')
def get_stats():
    return jsonify({"reps": counter, "squats": squat_counter, "heart_rate": get_heart_rate()})
@app.route('/reset_count')
def reset_count():
    global counter
    counter=0
    return "Counter reset!"
if __name__ == '__main__':
    app.run(debug=True)