# app.py
import cv2
import mediapipe as mp
from flask import Flask, jsonify, Response
from threading import Thread

# Import your feedback functions
from Squat_feedback import squat_feedback
from feedback_color import draw_feedback

app = Flask(__name__)

class VideoProcessor:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.cap = cv2.VideoCapture(0)
        self.state = 'up'
        self.running = False
        self.thread = None

    def start_processing(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                time_feedback, depth_feedback, self.state = squat_feedback(results.pose_landmarks.landmark, self.state)
                color = draw_feedback(frame, results.pose_landmarks, time_feedback, depth_feedback)
                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                               self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                                               self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2))

            cv2.imshow('Pose Estimation', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def stop_processing(self):
        self.running = False
        if self.thread:
            self.thread.join()

video_processor = VideoProcessor()

@app.route('/start', methods=['POST'])
def start_video():
    if not video_processor.running:
        video_processor.thread = Thread(target=video_processor.start_processing)
        video_processor.thread.start()
        return jsonify({"message": "Video processing started"})
    return jsonify({"message": "Video processing already running"})

@app.route('/stop', methods=['POST'])
def stop_video():
    video_processor.stop_processing()
    return jsonify({"message": "Video processing stopped"})

@app.route('/video_feed')
def video_feed():
    def generate():
        while video_processor.running:
            ret, frame = video_processor.cap.read()
            if not ret:
                break
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def home():
    return "Welcome to the RepRight Video Processing API!"

if __name__ == '__main__':
    app.run(debug=True)
