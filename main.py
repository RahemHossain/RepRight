import cv2
import mediapipe as mp
import time
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback_box  # Import feedback UI function

app = Flask(__name__)

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize state
state = 'up'

cap = cv2.VideoCapture(0)

depth_feedback = 'not_deep_enough'
time_feedback = None
tolorance_feedback = None
feedback_text = None
stored_feedback_text = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Get feedback for squats (with timing and depth)
        time_feedback, depth_feedback, tolorance_feedback, state = squat_feedback(results.pose_landmarks.landmark, state, tolorance_feedback, depth_feedback, time_feedback)

        # Create feedback text based on the feedback
        if state == 'up' and time_feedback is not None and depth_feedback is not None and tolorance_feedback is not None:
            stored_feedback_text = f"Timing: {time_feedback}\n Depth: {depth_feedback}\n Knee Alignment: {tolorance_feedback}"

        # Draw the skeleton
        color = (0, 255, 0)  # Green for good form by default
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

        # Draw feedback box if a rep is complete
        if stored_feedback_text and state == 'up':
            is_good_rep = 'good_depth' in stored_feedback_text and 'good_duration' in stored_feedback_text
            draw_feedback_box(frame, stored_feedback_text, is_good_rep)



    # Show the frame with feedback
    cv2.imshow('Pose Estimation', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cap.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
