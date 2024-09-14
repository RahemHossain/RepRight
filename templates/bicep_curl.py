from angle_calc import calculate_angle

def bicep_curl_feedback(landmarks):
    # Get necessary landmarks (right shoulder, right elbow, right wrist)
    shoulder = landmarks['right_shoulder']
    elbow = landmarks['right_elbow']
    wrist = landmarks['right_wrist']

    # Calculate the forearm angle (between shoulder, elbow, and wrist)
    forearm_angle = calculate_angle(shoulder, elbow, wrist)

    # Provide feedback based on the forearm angle
    if forearm_angle > 160:  # Arbitrary threshold for "not curled enough"
        feedback_text = "Not enough curl"
    elif forearm_angle < 30:  # Arbitrary threshold for "curled too much"
        feedback_text = "Too much curl"
    else:
        feedback_text = "Good form"

    return feedback_text
