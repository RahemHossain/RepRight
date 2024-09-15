import cv2
from bicep_curl import check_bicep_curl, draw_feedback_box
from angle_calc import calculate_angle
import mediapipe as mp

# Initialize mediapipe pose estimation
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


# Function to extract the necessary pose landmarks
def get_pose_landmarks(image):
    # Convert the image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Process the image to detect the pose
    result = pose.process(image_rgb)
    # Return the landmarks if detected
    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        return [(int(lm.x * image.shape[1]), int(lm.y * image.shape[0])) for lm in landmarks]
    return None


def bicep_curl_main():
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Get pose landmarks from the frame
        landmarks = get_pose_landmarks(frame)

        if landmarks:
            # Get feedback for bicep curls for both arms
            left_feedback, right_feedback = check_bicep_curl(landmarks)
            is_good_form_left = "Good form" in left_feedback
            is_good_form_right = "Good form" in right_feedback

            # Draw feedback on the screen for both arms
            draw_feedback_box(frame, left_feedback, is_good_form_left, 50)
            draw_feedback_box(frame, right_feedback, is_good_form_right, 150)

        # Display the frame
        cv2.imshow('Bicep Curl Feedback', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    bicep_curl_main()
