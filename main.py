from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback

app = Flask(__name__)

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize state
state = 'up'


def generate_frames():
    global state
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            # Get feedback for squats (with timing and depth)
            time_feedback, depth_feedback, state = squat_feedback(results.pose_landmarks.landmark, state)

            # Draw feedback with color-coded skeleton
            color = draw_feedback(frame, results.pose_landmarks, time_feedback, depth_feedback)

            # Draw the skeleton in the respective color
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame = buffer.tobytes()

        # Yield the frame in the format required by the HTTP response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
