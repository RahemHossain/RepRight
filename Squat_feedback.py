# squat.py
import time
from angle_calc import calculate_angle
import mediapipe as mp

mp_pose = mp.solutions.pose

# Initialize global variables for timing and depth
start_time = None
end_time = None
depth_feedback = 'not_deep_enough'  # Default depth feedback

def squat_feedback(landmarks, state):
    global start_time, end_time, depth_feedback

    # Get coordinates for hip, knee, and ankle
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

    # Calculate the knee angle
    knee_angle = calculate_angle(hip, knee, ankle)

    # Check for squat start
    if knee_angle < 160 and state == 'up':  # Start of a squat (moving down)
        state = 'down'
        start_time = time.time()
        depth_feedback = 'not_deep_enough'  # Reset depth feedback
        return None, None, state  # Keep skeleton white while squatting

    # Check for squat end
    elif knee_angle > 160 and state == 'down':  # End of a squat (moving up)
        state = 'up'
        end_time = time.time()

        # Calculate squat duration
        squat_duration = end_time - start_time

        # Provide timing feedback
        if squat_duration < 2.0:
            time_feedback = 'too_fast'
        else:
            time_feedback = 'good_duration'

        # Provide depth feedback
        if depth_feedback == 'not_deep_enough':
            print("Squat too shallow")
        elif depth_feedback == 'too_deep':
            print("Squat too deep")
        else:
            print("Good squat depth")

        print(f"Timing feedback: {time_feedback}")
        return time_feedback, depth_feedback, state

    # Check for depth while in the 'down' state
    if state == 'down':
        if knee_angle < 80:  # Depth too deep
            depth_feedback = 'too_deep'
        elif knee_angle >= 80 and knee_angle <= 160:  # Depth good
            depth_feedback = 'good_depth'

    return None, None, state  # Default state is white (while standing up)
