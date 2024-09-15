import cv2
from angle_calc import calculate_angle
import mediapipe as mp

# Initialize mediapipe pose estimation
mp_pose = mp.solutions.pose

# Function to check bicep curl feedback
def check_bicep_curl(pose_landmarks):
    # Calculate angles for left and right arms
    left_forearm_angle = calculate_angle(pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         pose_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                         pose_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])

    right_forearm_angle = calculate_angle(pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          pose_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                          pose_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])

    # Define thresholds for a good bicep curl
    min_curl_angle = 40  # Represents deep enough curl
    max_curl_angle = 150  # Represents too little curl

    # Feedback for left arm
    if left_forearm_angle < min_curl_angle:
        left_feedback = "Left arm: Over-curling"
    elif left_forearm_angle > max_curl_angle:
        left_feedback = "Left arm: Not curling enough"
    else:
        left_feedback = "Left arm: Good form"

    # Feedback for right arm
    if right_forearm_angle < min_curl_angle:
        right_feedback = "Right arm: Over-curling"
    elif right_forearm_angle > max_curl_angle:
        right_feedback = "Right arm: Not curling enough"
    else:
        right_feedback = "Right arm: Good form"

    return left_feedback, right_feedback

# Function to draw feedback box on the screen
def draw_feedback_box(image, feedback_text, is_good_form, y_offset):
    # Set color depending on form quality
    color = (0, 255, 0) if is_good_form else (0, 0, 255)

    # Draw rectangle for feedback box
    cv2.rectangle(image, (10, y_offset), (400, y_offset + 40), color, -1)

    # Put feedback text inside the box
    cv2.putText(image, feedback_text, (20, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
