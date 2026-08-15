from flask import Flask, Response,render_template,jsonify,request,session,redirect
import cv2
import mediapipe as mp
import numpy as np
from angle_utils import calculate_angle,is_visible
import mysql.connector
from smartwatch_api import get_heart_rate
import os
from dotenv import load_dotenv
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.environ.get("DB_PASSWORD"),
    database="smartfit_db"
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
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
selected_exercise = "bicep_curl"
camera_on = True
min_squat_angle = 180
squat_feedback = ""
min_angle_r = 180
min_angle_l = 180
bicep_feedback = ""
connections = [
    (11, 12), (12, 14), (14, 16), (11, 13), (13, 15),
    (11, 23), (12, 24), (23, 24),
    (24, 26), (26, 28), (23, 25), (25, 27)
]

def generate_frames():
    global frame_timestamp_ms, counter, stage_right,stage_left,squat_counter,stage_squat,selected_exercise,camera_on,cap,min_squat_angle,squat_feedback,min_angle_r,min_angle_l,bicep_feedback
    while True:
        if not camera_on:
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Camera is paused", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue
        ret, frame = cap.read()
        if not ret:
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        if result.pose_landmarks:
            h, w, _ = frame.shape
            for pose in result.pose_landmarks:
                if selected_exercise == "bicep_curl" :
                    heart_rate = get_heart_rate()
                    if heart_rate > 150 :
                        cv2.putText(frame, "Heart rate is high - consider slowing down", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    if heart_rate < 50 :
                        cv2.putText(frame, "Heart rate is low - check in with yourself", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    
                    shoulder_r, elbow_r, wrist_r = pose[12], pose[14], pose[16]
                    if is_visible(shoulder_r, elbow_r, wrist_r):
                        angle_r = calculate_angle(shoulder_r, elbow_r, wrist_r)
                        
                        # Track deepest curl while arm is in "up" (curled) phase
                        if stage_right == "up" and angle_r < min_angle_r:
                            min_angle_r = angle_r

                        if angle_r < 90 and stage_right == "down":
                            stage_right  = "up"
                            min_angle_r = angle_r

                        if angle_r > 160 and stage_right  == "up":
                            stage_right = "down"
                            counter = counter + 1
                            if min_angle_r < 30:
                                bicep_feedback = "Great curl!"
                            elif min_angle_r < 50:
                                bicep_feedback = "Good curl!"
                            else:
                                bicep_feedback = "Curl higher for full range"
                            min_angle_r = 180
                        cv2.putText(frame, "R Angle: " + str(int(angle_r)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    shoulder_l,elbow_l,wrist_l= pose[11],pose[13],pose[15]
        
                    if is_visible(shoulder_l, elbow_l, wrist_l):
                        angle_l= calculate_angle(shoulder_l,elbow_l,wrist_l)
                                            
                        if stage_left == "up" and angle_l < min_angle_l:
                            min_angle_l = angle_l

                        if angle_l < 90 and stage_left == "down":
                            stage_left  = "up"
                            min_angle_l = angle_l

                        if angle_l > 160 and stage_left == "up":
                            stage_left = "down"
                            counter = counter + 1
                            if min_angle_l < 30:
                                bicep_feedback = "Great curl!"
                            elif min_angle_l < 50:
                                bicep_feedback = "Good curl!"
                            else:
                                bicep_feedback = "Curl higher for full range"
                            min_angle_l = 180
                        cv2.putText(frame, "L Angle: " + str(int(angle_l)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    cv2.putText(frame, "Rep Count: "+str(counter), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "BPM: "+str(heart_rate), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, bicep_feedback, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 230, 118), 2)

                if selected_exercise == "squat" : 
                    
                    heart_rate = get_heart_rate()
                    if heart_rate > 150:
                        cv2.putText(frame, "Heart rate is high - consider slowing down", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    if heart_rate < 50:
                        cv2.putText(frame, "Heart rate is low - check in with yourself", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    hip,knee,ankle = pose[24],pose[26],pose[28]
                    if is_visible(hip,knee,ankle):
                        angle_knee=calculate_angle(hip,knee,ankle )
                        if stage_squat == "down" and angle_knee < min_squat_angle:
                            min_squat_angle = angle_knee

                        if angle_knee < 140 and stage_squat == "up":
                            stage_squat = "down"
                            min_squat_angle = angle_knee

                        if angle_knee > 160 and stage_squat == "down":
                            stage_squat = "up"
                            squat_counter = squat_counter + 1
                            if min_squat_angle < 70:
                                squat_feedback = "Great depth!"
                            elif min_squat_angle < 90:
                                squat_feedback = "Good squat!"
                            else:
                                squat_feedback = "Try to squat lower"
                            min_squat_angle = 180

                        cv2.putText(frame, "knee Angle: " + str(int(angle_knee)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "squat count: "+str(squat_counter), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "BPM: "+str(heart_rate), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, squat_feedback, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 230, 118), 2)

                for start_idx, end_idx in connections:
                    start = pose[start_idx]
                    end = pose[end_idx]
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, start_point, end_point, (0, 0, 255), 2)

                for lm in pose:
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)


        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def home():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/save_workout')
def save_workout():
    global counter,squat_counter
    username = session['username']
    duration = request.args.get('duration')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    user_id = user[0]
    cursor=conn.cursor()
    cursor.execute("INSERT INTO workouts (exercise,reps,date,user_id,duration) VALUES(%s,%s,%s,%s,%s)",("bicep_curl",counter,date.today(),user_id,duration))
    cursor.execute("INSERT INTO workouts (exercise,reps,date,user_id,duration) VALUES(%s,%s,%s,%s,%s)",("squat",squat_counter,date.today(),user_id,duration))
    conn.commit()
    counter=0
    squat_counter=0
    return "workout saved!"
@app.route('/get_stats')
def get_stats():
    return jsonify({"reps": counter, "squats": squat_counter, "heart_rate": get_heart_rate()})
@app.route('/reset_count')
def reset_count():
    global counter
    counter=0
    return "Counter reset!"
@app.route('/history')
def history():
    username = session['username']
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    user_id = user[0]

    cursor.execute("SELECT * FROM workouts WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    bicep_dates = []
    bicep_reps = []
    squat_dates = []
    squat_reps = []
    for row in data:
        if row[1] == "bicep_curl":
            bicep_dates.append(str(row[3]))
            bicep_reps.append(row[2])
        if row[1] == "squat":
            squat_dates.append(str(row[3]))
            squat_reps.append(row[2])
    return render_template('history.html', workouts=data, bicep_dates=bicep_dates, bicep_reps=bicep_reps, squat_dates=squat_dates, squat_reps=squat_reps)
@app.route('/selected_exercise/<exercise>')
def select_exercise(exercise):
    global selected_exercise
    selected_exercise=exercise
    return "selected: " + exercise
@app.route('/toggle_camera')
def toggle_camera():
    global camera_on,cap
    camera_on = not camera_on
    if camera_on:
        cap = cv2.VideoCapture(0)
    else: 
        cap.release()
    return "camera"
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try: 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            return redirect('/login')
        except mysql.connector.IntegrityError:
            return render_template('register.html', error="Username already taken. Please choose another.")
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect('/')
        else:
            return "Invalid username or password"

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/login')
if __name__ == '__main__':
    app.run(debug=True)