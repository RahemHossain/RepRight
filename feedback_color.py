import cv2

def draw_feedback(frame, landmarks, time_feedback, depth_feedback, tolorance_feedback):
    if time_feedback == 'good_duration' and depth_feedback == 'good_depth' and tolorance_feedback == True:
        color = (0, 255, 0)  # Green for good form and timing
    elif time_feedback == 'too_fast':
        color = (255, 0, 0)  # Red for too fast
    elif depth_feedback == 'too_deep':
        color = (0, 165, 255)  # Orange for too deep
    elif depth_feedback == 'not_deep_enough':
        color = (255, 0, 0)  # Red for not deep enough
    elif tolorance_feedback == False:
        color = (255, 0, 255)
    else:
        color = (255, 255, 255)  # White while standing up

    return color


def draw_feedback_box(frame, feedback_text, is_good_rep):
    # Set the box color based on whether it's a good rep or not
    box_color = (0, 255, 0) if is_good_rep else (0, 0, 255)  # Green for good rep, red for bad rep

    # Set the text color (white for visibility)
    text_color = (255, 255, 255)

    # Set box background transparency (alpha channel)
    alpha = 0.6  # Semi-transparent background

    # Define the position and size of the box
    box_x, box_y, box_width, box_height = 50, 50, 400, 150  # Adjust these values to fit your UI design

    # Create an overlay for transparency
    overlay = frame.copy()  # Copy the frame to create an overlay
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_width, box_y + box_height), box_color, -1)

    # Apply the semi-transparent background
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Draw the shadow effect (slightly offset from the box)
    shadow_offset = 10
    shadow_color = (50, 50, 50)  # Dark shadow color
    cv2.rectangle(frame, (box_x + shadow_offset, box_y + shadow_offset),
                  (box_x + box_width + shadow_offset, box_y + box_height + shadow_offset), shadow_color, -1)

    # Draw the main box with rounded corners (border radius effect)
    border_radius = 20
    cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), box_color, border_radius)

    # Add feedback text inside the box
    font_scale = 1.0
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Split the feedback text into multiple lines
    lines = feedback_text.split('\n')
    for i, line in enumerate(lines):
        text_y = box_y + 40 + (i * 30)  # Position the text below the top of the box
        cv2.putText(frame, line, (box_x + 20, text_y), font, font_scale, text_color, thickness)
