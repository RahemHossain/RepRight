import cv2
import mediapipe as mp
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Get feedback for squats
        feedback = squat_feedback(results.pose_landmarks.landmark)

        # Draw feedback with color-coded skeleton
        draw_feedback(frame, results.pose_landmarks, feedback)
    cv2.imshow('Pose Estimation', frame)


    #ends code
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
