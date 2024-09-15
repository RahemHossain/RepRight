# squat.py
import time
from angle_calc import calculate_angle
import mediapipe as mp
import math


mp_pose = mp.solutions.pose

# Initialize global variables for timing and depth
start_time = None
end_time = None
  # Default depth feedback





def squat_feedback(landmarks, state, tolerance_feedback, depth_feedback, time_feedback):
    global start_time, end_time

    # Get coordinates for left and right knee
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]

    # Get coordinates for hip and ankle for both legs
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

    # Calculate knee angles
    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

    # Check for squat start
    if left_knee_angle < 170 and right_knee_angle < 170 and state == 'up':  # Start of a squat (moving down)
        state = 'down'
        start_time = time.time()
        depth_feedback = 'Not Deep Enough'  # Reset depth feedback
        tolerance_feedback = None  # Reset tolerance feedback
        return time_feedback, depth_feedback, tolerance_feedback, state  # Keep skeleton white while squatting

    # Check for squat end
    elif left_knee_angle > 160 and right_knee_angle > 160 and state == 'down':  # End of a squat (moving up)
        state = 'up'
        end_time = time.time()

        # Calculate squat duration
        squat_duration = end_time - start_time

        # Provide timing feedback
        if squat_duration < 2.0:
            time_feedback = 'Too Fast'
        else:
            time_feedback = 'Good Duration'

        return time_feedback, depth_feedback, tolerance_feedback, state
    # Check for depth while in the 'down' state
    if state == 'down':
        if left_knee_angle < 75 and right_knee_angle < 75 and (
                depth_feedback == 'Good Depth' or depth_feedback == 'Not Deep Enough'):  # Depth too deep
            depth_feedback = 'Too Deep'
        elif (left_knee_angle >= 75 and left_knee_angle <= 130) and (
                right_knee_angle >= 75 and right_knee_angle <= 130) and depth_feedback == 'Not Deep Enough':  # Depth good
            depth_feedback = 'Good Depth'
            # Only update depth_feedback here if depth is too shallow
        elif depth_feedback != 'Too Deep' and depth_feedback != 'Good Depth':
            depth_feedback = 'Not Deep Enough'

        # Check knee alignment only while squatting
        if tolerance_feedback is None:
            tolerance_feedback = check_knee_alignment(left_knee_angle, right_knee_angle)

    return time_feedback, depth_feedback, tolerance_feedback, state




# utils.py or the same file
def check_knee_alignment(left_knee_angle, right_knee_angle, tolerance=30):
    """Checks if both knees are aligned (i.e., not too far apart)."""
    distance = math.fabs(left_knee_angle - right_knee_angle)
    return distance < tolerance
