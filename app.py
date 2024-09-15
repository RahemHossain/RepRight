from flask import Flask, Response
from flask_cors import CORS
import cv2
import mediapipe as mp
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback_box  # Import feedback UI function
import signal

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Video capture
cap = cv2.VideoCapture(0)

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

# Signal handler to ensure cleanup on termination
def signal_handler(sig, frame):
    cleanup_resources()
    print("Exiting cleanly...")
    exit(0)

# Capture termination signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def generate_frames():
    global state, depth_feedback, time_feedback, tolerance_feedback
    global stored_feedback_text1, stored_feedback_text2, stored_feedback_text3
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
            time_feedback, depth_feedback, tolerance_feedback, state = squat_feedback(
                results.pose_landmarks.landmark, state, tolerance_feedback, depth_feedback, time_feedback)

            # Create feedback text based on the feedback
            if state == 'up' and all([time_feedback, depth_feedback, tolerance_feedback]):
                stored_feedback_text1 = f"Timing: {time_feedback}"
                stored_feedback_text2 = f"Depth: {depth_feedback}"
                stored_feedback_text3 = f"Knee Alignment: {tolerance_feedback}"
                feedback_displayed = True  # Set the flag to True to display feedback
            else:
                feedback_displayed = False  # Reset the flag if not in 'up' position

            # Draw the skeleton
            color = (0, 255, 0)  # Green for good form by default
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

            # Draw feedback boxes if feedback is displayed
            if feedback_displayed:
                is_good_depth = 'Good Depth' in depth_feedback.lower() if isinstance(depth_feedback, str) else False
                is_good_time = 'Good Duration' in time_feedback.lower() if isinstance(time_feedback, str) else False
                is_good_knees = tolerance_feedback
                draw_feedback_box(frame, stored_feedback_text1, is_good_time, 50)
                draw_feedback_box(frame, stored_feedback_text2, is_good_depth, 150)
                draw_feedback_box(frame, stored_feedback_text3, is_good_knees, 250)

        # Encode the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        # Yield the output frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
        app.run(debug=True)
    finally:
        cleanup_resources()  # Make sure resources are cleaned up on shutdown
