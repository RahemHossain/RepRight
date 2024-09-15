import cv2
import mediapipe as mp
from bicep_curl import check_bicep_curl
from feedback_color import draw_feedback_box  # Import feedback UI function

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Video capture
cap = cv2.VideoCapture(0)

# Initialize state variables
state_left = 'up'
state_right = 'up'
depth_feedback_left = 'not deep enough'
depth_feedback_right = 'not deep enough'
time_feedback_left = None
time_feedback_right = None
tolerance_feedback_left = None
tolerance_feedback_right = None

stored_feedback_text_left = None
stored_feedback_text_right = None

while True:
    success, frame = cap.read()
    if not success:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Get feedback for bicep curls (with timing and depth)
        time_feedback_left, depth_feedback_left, tolerance_feedback_left, state_left = check_bicep_curl(
            results.pose_landmarks.landmark, state_left, tolerance_feedback_left, depth_feedback_left,
            time_feedback_left, "left")

        time_feedback_right, depth_feedback_right, tolerance_feedback_right, state_right = check_bicep_curl(
            results.pose_landmarks.landmark, state_right, tolerance_feedback_right, depth_feedback_right,
            time_feedback_right, "right")

        # Create feedback text based on the feedback for both arms
        if state_left == 'up' and all([time_feedback_left, depth_feedback_left, tolerance_feedback_left]):
            stored_feedback_text_left = f"Left Arm: Timing: {time_feedback_left}, Depth: {depth_feedback_left}, Tolerance: {tolerance_feedback_left}"

        if state_right == 'up' and all([time_feedback_right, depth_feedback_right, tolerance_feedback_right]):
            stored_feedback_text_right = f"Right Arm: Timing: {time_feedback_right}, Depth: {depth_feedback_right}, Tolerance: {tolerance_feedback_right}"

        # Draw the skeleton
        color = (0, 255, 0)  # Green for good form by default
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

        # Draw feedback boxes if feedback is displayed
        if state_left == 'up':
            is_good_depth_left = 'good depth' in depth_feedback_left.lower()
            is_good_time_left = 'good duration' in time_feedback_left.lower()
            is_good_knees_left = tolerance_feedback_left.lower() == 'good alignment'
            draw_feedback_box(frame, stored_feedback_text_left, is_good_depth_left, 50)

        if state_right == 'up':
            is_good_depth_right = 'good depth' in depth_feedback_right.lower()
            is_good_time_right = 'good duration' in time_feedback_right.lower()
            is_good_knees_right = tolerance_feedback_right.lower() == 'good alignment'
            draw_feedback_box(frame, stored_feedback_text_right, is_good_depth_right, 150)

    # Display the resulting frame
    cv2.imshow('Bicep Curl Feedback', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
