import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from angle_utils import calculate_angle

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
counter=0
stage="down"
connections = [
    (11, 12), (12, 14), (14, 16), (11, 13), (13, 15),
    (11, 23), (12, 24), (23, 24),
    (24, 26), (26, 28), (23, 25), (25, 27)
]
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
    frame_timestamp_ms += 33

    if result.pose_landmarks:
        h, w, _ = frame.shape
        for pose in result.pose_landmarks:
            shoulder, elbow, wrist = pose[12], pose[14], pose[16]
            for start_idx, end_idx in connections:
                start = pose[start_idx]
                end = pose[end_idx]
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(frame, start_point, end_point, (0, 0, 255), 2)
            angle = calculate_angle(shoulder, elbow, wrist)
               
            if angle < 50 and stage == "down":
                stage = "up"
            if angle> 160 and stage == "up":
                stage="down"
                counter=counter+1
            for lm in pose:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
            cv2.putText(frame, str(int(angle)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame,str(counter), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow('Pose Detection', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    if key == ord('r'):
        counter=0
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)