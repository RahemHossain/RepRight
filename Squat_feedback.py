from angle_calc import calculate_angle
import mediapipe as mp

mp_pose = mp.solutions.pose


def squat_feedback(landmarks):
    # Get coordinates for hip, knee, and ankle
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

    # Calculate the knee angle
    knee_angle = calculate_angle(hip, knee, ankle)

    # Provide feedback based on the knee angle
    if knee_angle < 80:
        return 'too_deep'
    elif knee_angle > 160:
        return 'not_deep_enough'
    else:
        return 'good_form'