from flask import Flask, Response
from flask_cors import CORS
import cv2
import mediapipe as mp
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback_box  # Import feedback UI function
import signal
import logging
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Error: Could not open video source.")

# Initialize state variables
state = 'up'
depth_feedback = 'not deep enough'
time_feedback = None
tolerance_feedback = None

stored_feedback_text1 = None
stored_feedback_text2 = None
stored_feedback_text3 = None

# Cleanup function to release resources
def cleanup_resources():
    global cap
    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    logging.info("Resources cleaned up.")

# Signal handler to ensure cleanup on termination
def signal_handler(sig, frame):
    cleanup_resources()
    logging.info("Exiting cleanly...")
    exit(0)

# Capture termination signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def generate_frames():
    global state, depth_feedback, time_feedback, tolerance_feedback
    global stored_feedback_text1, stored_feedback_text2, stored_feedback_text3
    feedback_displayed = False
    last_state = 'up'

    with mp_pose.Pose() as pose:
        while True:
            if not cap.isOpened():
                break

            success, frame = cap.read()
            if not success:
                logging.error("Failed to read frame from video capture.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

            if results.pose_landmarks:
                time_feedback, depth_feedback, tolerance_feedback, new_state = squat_feedback(
                    results.pose_landmarks.landmark, state, tolerance_feedback, depth_feedback, time_feedback)

                # Check if a rep has been completed
                if new_state == 'up' and last_state == 'down':
                    stored_feedback_text1 = f"Timing: {time_feedback}"
                    stored_feedback_text2 = f"Depth: {depth_feedback}"
                    stored_feedback_text3 = f"Knee Alignment: {tolerance_feedback}"
                    feedback_displayed = True
                    logging.info(f"Rep completed: {stored_feedback_text1}, {stored_feedback_text2}, {stored_feedback_text3}")

                # Check if a new rep has started
                if new_state == 'down' and last_state == 'up':
                    feedback_displayed = False

                last_state = new_state
                state = new_state

                # Draw the skeleton
                color = (0, 255, 0)
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

                # Draw feedback boxes if feedback is displayed
                if feedback_displayed:
                    is_good_depth = 'Good Depth' in depth_feedback if depth_feedback else False
                    is_good_time = 'Good Duration' in time_feedback if time_feedback else False
                    is_good_knees = tolerance_feedback if tolerance_feedback else False
                    draw_feedback_box(frame, stored_feedback_text1, is_good_time, 50)
                    draw_feedback_box(frame, stored_feedback_text2, is_good_depth, 150)
                    draw_feedback_box(frame, stored_feedback_text3, is_good_knees, 250)

            # Encode the frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Failed to encode frame to JPEG.")
                continue
            frame = buffer.tobytes()

            # Yield the output frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Add a small sleep to avoid high CPU usage
            time.sleep(0.01)

    cleanup_resources()

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def home():
    return "Welcome to the RepRight Video Processing API!"

if __name__ == '__main__':
    try:
        app.run(debug=True, threaded=False)
    finally:
        cleanup_resources()  # Make sure resources are cleaned up on shutdown
