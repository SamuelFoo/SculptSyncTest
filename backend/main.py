import cv2
from flask import Flask, Response

app = Flask(__name__)


# Route to stream video feed
@app.route("/video_feed")
def video_feed():
    def generate_frames():
        cap = cv2.VideoCapture(0)  # Capture video from the webcam
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()

                # Stream frame
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        cap.release()

    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
