from flask import Flask, Response, render_template
from flask_cors import CORS
import cv2
import mediapipe as mp
import time
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback_box  # Import feedback UI function

app = Flask(__name__)
CORS(app)  # Enable CORS to allow React frontend to access the video feed

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize state
state = 'up'
depth_feedback = 'not deep enough'
time_feedback = None
tolerance_feedback = None

# Video capture
cap = cv2.VideoCapture(0)

stored_feedback_text1 = None
stored_feedback_text2 = None
stored_feedback_text3 = None

# Video capture

def generate_frames():
    global state, depth_feedback, time_feedback, tolerance_feedback, stored_feedback_text1, stored_feedback_text2, stored_feedback_text3
    feedback_displayed = False  # Flag to track if feedback is displayed

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            # Get feedback for squats (with timing and depth)
            time_feedback, depth_feedback, tolorance_feedback, state = squat_feedback(
                results.pose_landmarks.landmark, state, tolorance_feedback, depth_feedback, time_feedback)

            # Create feedback text based on the feedback
            if state == 'up' and time_feedback is not None and depth_feedback is not None and tolorance_feedback is not None:
                stored_feedback_text1 = f"Timing: {time_feedback}\n"
                stored_feedback_text2 = f"Depth: {depth_feedback}\n"
                stored_feedback_text3 = f"Knee Alignment: {tolorance_feedback}\n"
                feedback_displayed = True  # Set the flag to True to display feedback
            else:
                feedback_displayed = False  # Reset the flag if not in 'up' position

            # Draw the skeleton
            color = (0, 255, 0)  # Green for good form by default
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

            # Draw feedback boxes if feedback is displayed
            if feedback_displayed:
                is_good_depth = 'good depth' in depth_feedback
                is_good_time = 'good duration' in time_feedback
                is_good_knees = tolorance_feedback
                draw_feedback_box(frame, stored_feedback_text1, is_good_time, 50)
                draw_feedback_box(frame, stored_feedback_text2, is_good_depth, 150)
                draw_feedback_box(frame, stored_feedback_text3, is_good_knees, 250)

        # Encode the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the output frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@app.route('/')
def index():
    # Render HTML template to display the video stream
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)