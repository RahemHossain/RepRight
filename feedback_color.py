# draw.py or in main.py


def draw_feedback(frame, landmarks, time_feedback, depth_feedback):
    if time_feedback == 'good_duration' and depth_feedback == 'good_depth':
        color = (0, 255, 0)  # Green for good form and timing
    elif time_feedback == 'too_fast':
        color = (255, 0, 0)  # Red for too fast
    elif depth_feedback == 'too_deep':
        color = (0, 165, 255)  # Orange for too deep
    elif depth_feedback == 'not_deep_enough':
        color = (255, 0, 0)  # Red for not deep enough
    else:
        color = (255, 255, 255)  # White while standing up

    return color

