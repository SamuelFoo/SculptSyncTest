"use client";

import { useRef, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils,
} from "@mediapipe/tasks-vision";

const VideoFeed = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const router = useRouter();
  const [exercise, setExercise] = useState("");
  const [reps, setReps] = useState(0);
  const [selectedCameraId, setCameraId] = useState(0);
  const [cameraOptions, setCameraOptions] = useState([]);
  const displayHeight = 480;
  const displayWidth = 640;

  useEffect(() => {
    // Get exercise query parameters from the URL
    const query = new URLSearchParams(window.location.search);
    const exerciseName = query.get("exercise");

    if (exerciseName) {
      setExercise(decodeURIComponent(exerciseName));
    }

    getConnectedCameras();
  }, []);

  useEffect(() => {
    // Disable prediction, if any, before restarting pipeline
    videoRef.current.removeEventListener("loadeddata", () => { });
    startPipeline(selectedCameraId);
  }, [selectedCameraId])

  // Start webcam
  const startPipeline = (cameraId) => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      Promise.all([
        navigator.mediaDevices.getUserMedia({ video: { deviceId: cameraId } }),
        createPoseLandmarker()
      ])
        .then((promises) => {
          videoRef.current.srcObject = promises[0];
          videoRef.current.addEventListener("loadeddata", () => predictWebcam(promises[1]));
        })
        .catch((err) => {
          console.error("Error accessing camera: ", err);
        });
    } else {
      console.error("getUserMedia not supported");
    }
  };

  // Start pose landmark
  const createPoseLandmarker = async () => {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
    );
    const pose = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numPoses: 2,
    });

    return pose;
  };

  const calculateAngle = (a, b, c) => {
    const radians =
      Math.atan2(c[1] - b[1], c[0] - b[0]) -
      Math.atan2(a[1] - b[1], a[0] - b[0]);
    let angle = Math.abs((radians * 180.0) / Math.PI);

    if (angle > 180.0) {
      angle = 360 - angle;
    }

    return angle;
  };

  const predictWebcam = async (poseLandmarker) => {
    const canvasCtx = canvasRef.current.getContext("2d");
    const drawingUtils = new DrawingUtils(canvasCtx);
    let lastVideoTime = -1;

    let startTimeMs = performance.now();
    if (lastVideoTime !== videoRef.current.currentTime) {
      lastVideoTime = videoRef.current.currentTime;
      poseLandmarker.detectForVideo(videoRef.current, startTimeMs, (result) => {
        canvasCtx.save();
        canvasCtx.clearRect(
          0,
          0,
          canvasRef.current.width,
          canvasRef.current.height
        );
        for (const landmark of result.landmarks) {
          drawingUtils.drawLandmarks(landmark, {
            radius: (data) => DrawingUtils.lerp(data.from.z, -0.15, 0.1, 5, 1),
          });
          drawingUtils.drawConnectors(
            landmark,
            PoseLandmarker.POSE_CONNECTIONS
          );
        }
        canvasCtx.restore();
      });
    }

    // Call this function again to keep predicting when the browser is ready.
    if (videoRef.current) {
      window.requestAnimationFrame(() => predictWebcam(poseLandmarker));
    }
  };

  const handleHomeClick = () => {
    // Navigate to home page
    router.push("/");
  };

  const getConnectedCameras = () => {
    navigator.mediaDevices.enumerateDevices().then(function (devices) {
      const options = [];
      for (var i = 0; i < devices.length; i++) {
        var device = devices[i];
        if (device.kind === 'videoinput') {
          options.push({ value: device.deviceId, label: device.label || 'camera ' + (i + 1) })
        }
      };

      setCameraOptions(options);
    });
  }

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Top Bar with Home Button, Exercise, and Reps */}
      <div className="flex-none p-4 bg-gray-800 text-white flex items-center justify-between">
        <button
          onClick={handleHomeClick}
          className="text-lg font-semibold bg-gray-700 p-2 rounded"
        >
          Home
        </button>
        <div className="flex flex-col items-center flex-grow">
          <h1 className="text-2xl font-semibold">
            Current Exercise: {exercise}
          </h1>
        </div>
        <p className="text-4xl font-bold">Reps: {reps}</p>
      </div>

      {/* Video Feed Section */}
      <div className="flex flex-grow flex-col items-center justify-center">
        <div className="relative">
          <video
            ref={videoRef}
            autoPlay
            className="z-0 top-0 left-0 border-2 border-gray-700"
            width={displayWidth}
            height={displayHeight}
            onError={(e) => console.error("Video error:", e)}
          />
          <canvas
            className="absolute z-1 top-0 left-0 object-cover rounded-lg border-2 border-gray-700"
            id="output_canvas"
            width={displayWidth}
            height={displayHeight}
            ref={canvasRef}
          ></canvas>
        </div>
        <select value={selectedCameraId}
          onChange={e => setCameraId(e.target.value)}
        >
          {cameraOptions.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>

      {/* Feedback Box */}
      <div className="flex-none p-4 bg-gray-800 text-white rounded-t-lg shadow-lg">
        <h2 className="text-lg font-semibold">Feedback</h2>
        <div className="mt-2">
          <p id="comments" className="mt-1">
            No feedback yet
          </p>
        </div>
      </div>
    </div >
  );
};

export default VideoFeed;
