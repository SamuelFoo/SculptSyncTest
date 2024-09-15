import cv2
from flask import Flask, Response

app = Flask(__name__)

# For CSI camera
device_id = 0
camSet = f"nvarguscamerasrc sensor-id={device_id} ! video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"

# For USB camera
# camSet = 5

# Route to stream video feed
@app.route("/video_feed")
def video_feed():
    def generate_frames():
        cap = cv2.VideoCapture(camSet)  # Capture video from the webcam

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (640, 480))

            # Encode frame as JPEG
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Stream frame
            if ret:
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        cap.release()

    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
