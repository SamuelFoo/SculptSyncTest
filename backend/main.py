from enum import Enum
from flask import Flask, Response, stream_with_context
import cv2
import numpy as np
import requests

import mediapipe as mp
import numpy as np
from flask import Flask, Response

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

app = Flask(__name__)

rep_count = 0
rep_stage = None

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1], a[0] - b[0]
    )
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def draw_rep_counter(image, counter, rep_stage):
    # Render curl counter
    # Setup status box
    cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

    # Rep data
    cv2.putText(
        image,
        "REPS",
        (15, 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        str(counter),
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # rep_stage data
    cv2.putText(
        image,
        "rep_stage",
        (65, 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        rep_stage,
        (60, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

def process_frame(pose: mp.solutions.pose.Pose, frame):
    global rep_count, rep_stage

    # Recolor image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Make detection
    results = pose.process(image)

    # Recolor back to BGR
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Extract landmarks
    try:
        landmarks = results.pose_landmarks.landmark

        # Get coordinates
        shoulder = [
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
        ]
        elbow = [
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
        ]
        wrist = [
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y,
        ]

        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Visualize angle
        cv2.putText(
            image,
            str(angle),
            tuple(np.multiply(elbow, [640, 480]).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Curl counter logic
        if angle > 160:
            rep_stage = "down"
        if angle < 30 and rep_stage == "down":
            rep_stage = "up"
            rep_count += 1

    except:
        pass

    draw_rep_counter(image, rep_count, rep_stage)

    # Render detections
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(
            color=(245, 117, 66), thickness=2, circle_radius=2
        ),
        mp_drawing.DrawingSpec(
            color=(245, 66, 230), thickness=2, circle_radius=2
        ),
    )

    return image


def packet_extr(boundary_start, boundary_end, generator):
    class State(Enum):
        FINDING_START = 1
        FINDING_END = 2

    state = State.FINDING_START
    dataarray = bytearray()
    previous_buffer = bytearray()

    while True:
        if state == State.FINDING_START:
            j = previous_buffer.find(boundary_start)

            if j != -1:
                dataarray.extend(previous_buffer[j:])
                previous_buffer = bytearray()

                end_index = dataarray.find(boundary_end)
                if end_index != -1:
                    dataarray = dataarray[:end_index+len(boundary_end)]
                    yield dataarray
                    dataarray = bytearray()
                    state = State.FINDING_START
                    continue
                else:
                    state = State.FINDING_END
                    continue

            else:
                previous_buffer = bytearray()

                chunk = next(generator)

                if not chunk:
                    continue

                i = chunk.find(boundary_start)
                if i == -1:
                    continue
                else:
                    dataarray.extend(chunk[i:])

                    end_index = dataarray.find(boundary_end)
                    if end_index != -1:
                        dataarray = dataarray[:end_index+len(boundary_end)]
                        yield dataarray
                        dataarray = bytearray()
                        state = State.FINDING_START
                        continue
                    else:
                        state = State.FINDING_END
                        continue

        if state == State.FINDING_END:
            chunk = next(generator)
            end_index = chunk.find(boundary_end)
            if end_index != -1:
                cutoff = end_index+len(boundary_end)
                dataarray.extend(chunk[:cutoff])
                yield dataarray
                dataarray = bytearray()
                previous_buffer.extend(chunk[cutoff:])
                state = State.FINDING_START
                continue
            else:
                dataarray.extend(chunk)
                state = State.FINDING_END
                continue

def get_frame_from_stream(url):
    response = requests.get(url, stream=True)
    boundary_start = b'\xff\xd8'  # JPEG start
    boundary_end = b'\xff\xd9'    # JPEG end

    def packet_extr_helper():
        while True:
            chunk = response.raw.read(512 * 1024)
            yield chunk

    packet_generator = packet_extr(boundary_start, boundary_end, packet_extr_helper())
    for packet in packet_generator:
        frame = np.frombuffer(packet, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        
        if frame is not None:
            yield frame
            
def generate_processed_frames():
    video_url = 'http://localhost:5000/video_feed'

    with mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as pose:
        for frame in get_frame_from_stream(video_url):
            if frame is not None:
                processed_frame = process_frame(pose, frame)

                _, buffer = cv2.imencode('.jpg', processed_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/processed_feed')
def processed_feed():
    return Response(stream_with_context(generate_processed_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
