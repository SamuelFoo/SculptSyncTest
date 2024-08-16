"use client";

import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils,
} from "@mediapipe/tasks-vision";
import { useState, useRef } from "react";

const Livestream = () => {
  const [isWebcamOn, setIsWebcamOn] = useState(false);
  const videoRef = useRef(null);

  // Access the user camera and video.
  const getVideo = () => {
    navigator.mediaDevices
      .getUserMedia({
        video: { width: 1920, height: 1080 },
      })
      .then((stream) => {
        let video = videoRef.current;
        video.srcObject = stream;
        video.play();
      })
      .catch((err) => {
        console.error(err);
      });
  };

  function enableCam(event) {
    if (isWebcamOn === true) {
      setIsWebcamOn(false);
    } else {
      getVideo();
      setIsWebcamOn(true);
    }
  }

  return (
    <div className="text-white">
      <h1>Pose detection using the MediaPipe PoseLandmarker task</h1>
      <div>
        <button id="webcamButton" onClick={enableCam}>
          {isWebcamOn ? "DISABLE WEBCAM" : "ENABLE WEBCAM"}
        </button>
        {isWebcamOn && (
          <div className="relative">
            <video
              id="webcam"
              className="absolute"
              playsInline
              width="360"
              height="540"
              ref={videoRef}
            ></video>
            <canvas
              className="output_canvasabsolute left-0 top-0"
              id="output_canvas"
              width="360"
              height="540"
            ></canvas>
          </div>
        )}
      </div>
    </div>
  );
};

export default Livestream;
