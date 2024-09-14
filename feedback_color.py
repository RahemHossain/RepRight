# Option 1: Keep in main.py or create draw.py
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils

def draw_feedback(frame, landmarks, feedback):
    if feedback == 'good_form':
        color = (0, 255, 0)  # Green for good form
    elif feedback == 'too_deep':
        color = (0, 165, 255)  # Orange for too deep
    else:
        color = (0, 0, 255)  # Red for not deep enough

    # Draw the skeleton in the respective color
    mp_drawing.draw_landmarks(frame, landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                              mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))
