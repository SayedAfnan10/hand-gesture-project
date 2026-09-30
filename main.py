"""Coordinate the camera, detector, processor, recognizer, and two windows."""

import time

import cv2

import config
from modules.camera import Camera
from modules.display import CameraDisplay
from modules.gesture_explanation import GestureExplanation
from modules.gesture_recognizer import recognize_gesture
from modules.hand_detector import HandDetector
from modules.landmark_processor import process_landmarks


def main():
    camera_display = analysis_display = None
    detector = None
    try:
        camera_display = CameraDisplay(config.CAMERA_WINDOW_NAME, config.CAMERA_WINDOW_WIDTH,
                                       config.CAMERA_WINDOW_HEIGHT, 20, 40)
        analysis_display = GestureExplanation(config.ANALYSIS_WINDOW_NAME,
                                              config.ANALYSIS_WINDOW_WIDTH,
                                              config.ANALYSIS_WINDOW_HEIGHT,
                                              config.CAMERA_WINDOW_WIDTH + config.WINDOW_GAP + 20, 40)
        detector = HandDetector(config.MODEL_PATH, config.MAX_HANDS,
                                config.MIN_DETECTION_CONFIDENCE,
                                config.MIN_PRESENCE_CONFIDENCE,
                                config.MIN_TRACKING_CONFIDENCE)
        fps = 0.0
        previous_time = time.perf_counter()
        with Camera(config.CAMERA_INDEX, config.CAMERA_WIDTH, config.CAMERA_HEIGHT) as camera:
            while True:
                ok, frame = camera.read()
                if not ok or frame is None:
                    print("Camera frame could not be read; stopping safely.")
                    break
                if config.MIRROR_CAMERA:
                    frame = cv2.flip(frame, 1)
                now = time.perf_counter()
                timestamp_ms = int(now * 1000)
                hands = detector.detect(frame, timestamp_ms)
                recognition = None
                if hands:
                    processed = process_landmarks(hands[0]["landmarks"])
                    recognition = recognize_gesture(processed, hands[0]["handedness"])
                elapsed = max(now - previous_time, 1e-9)
                fps = 0.9 * fps + 0.1 * (1.0 / elapsed) if fps else 1.0 / elapsed
                previous_time = now
                camera_display.render(frame, hands, recognition, fps)
                analysis_display.render(recognition)
                if CameraDisplay.should_quit():
                    break
    except (RuntimeError, OSError, cv2.error) as error:
        print(f"Application stopped: {error}")
    finally:
        if detector is not None:
            detector.close()
        CameraDisplay.close_all()


if __name__ == "__main__":
    main()

