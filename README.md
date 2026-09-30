# AI-Based Real-Time Hand Gesture Recognition System

A modular Python desktop application that reads a webcam, detects up to two hands, processes MediaPipe's 21 landmarks, and classifies common gestures with interpretable geometric rules. It opens two separate OpenCV windows: the live camera and an analysis panel driven by the exact structured result returned by the recognizer.

## Features

- Live webcam capture with safe camera checks and cleanup.
- MediaPipe Hand Landmarker Tasks API in video mode; supports multiple hands and handedness labels.
- 21 landmarks, skeleton connections, and a hand bounding rectangle drawn over the video.
- Scale-relative finger extension and thumb/index geometry.
- Ten rule-based gestures and readable recognition reasons.
- A distinct, continuously updated explanation window; it does not classify gestures itself.
- Basic webcam-independent unit tests for processing and classification.
- Downloads the official task model to `models/hand_landmarker.task` the first time the program runs.

## Technologies and requirements

- Python 3.10–3.12 is recommended on Windows for broad wheel compatibility.
- OpenCV for webcam input, drawing, and the two windows.
- MediaPipe Tasks for hand landmark detection.
- NumPy for analysis-panel rendering.

TensorFlow and PyTorch are not used directly by this project. MediaPipe's task model is a separate asset downloaded at runtime. The project uses the current Tasks `HandLandmarker` video API, with monotonically increasing timestamps. See Google's [Hand Landmarker Python documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python) and [API reference](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/HandLandmarker).

## Project architecture

```text
Webcam frame
    -> HandDetector: MediaPipe 21-point landmarks for each hand
    -> landmark_processor: finger states and relative measurements
    -> gesture_recognizer: one structured result with gesture, reasons, and evidence
         -> CameraDisplay: video, landmarks, gesture, FPS
         -> GestureExplanation: finger states, pattern, reasoning, measurements
```

The explanation view receives the same dictionary as the camera display. It only formats fields such as `finger_states`, `pattern`, `reasons`, and `rule_steps`; it does not independently infer a gesture.

## Folder structure

```text
hand_gesture_project/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── models/                         # created at first run
│   └── hand_landmarker.task
├── modules/
│   ├── __init__.py
│   ├── camera.py
│   ├── display.py
│   ├── gesture_data.py
│   ├── gesture_explanation.py
│   ├── gesture_recognizer.py
│   ├── hand_detector.py
│   ├── landmark_processor.py
│   └── utils.py
└── tests/
    ├── __init__.py
    ├── test_gesture_recognizer.py
    └── test_landmark_processor.py
```

## Installation and run (Windows PowerShell)

Open PowerShell in the project directory and run:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks virtual-environment activation, run this for the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

On first launch, allow Python to access the webcam in Windows privacy settings. The program downloads the MediaPipe model once; internet access is needed for that first download. Subsequent launches reuse the local model.

## What to expect

Two independently titled windows appear and update in the same loop:

1. **AI Hand Gesture Recognition — Camera** — mirrored live image, detected hand skeleton and rectangle, current gesture, FPS, and quit instruction.
2. **Gesture Recognition Analysis** — finger extension states, five-bit pattern, reasons and rule flow from the actual classification, plus only the geometric measurements used by relevant rules.

Press **Q** while either OpenCV window is focused to quit. The webcam and detector are released when the app closes.

## Supported gestures and rules

The pattern order is **thumb, index, middle, ring, pinky**; `1` means extended. Patterns are derived by the processor, and certain gestures need extra scale-relative geometry.

| Gesture | Expected pattern | Recognition condition | Window 1 | Window 2 |
|---|---|---|---|---|
| Fist | `00000` | All five processor states folded. | Shows **FIST** over the landmarked hand. | Shows five folded states and the all-folded rule reason. |
| Open Palm | `11111` | All states extended and thumb/index tips are not close enough for OK. | Shows **OPEN PALM**. | Shows five extended states, pattern, and pattern-match reasons. |
| Peace / Victory | `01100` | Index and middle extended; thumb, ring, and pinky folded. | Shows **PEACE / VICTORY**. | Shows the same states and matching rule. |
| Thumbs Up | `10000` | Other four folded; thumb tip is above wrist by more than 0.28 palm heights. | Shows **THUMBS UP**. | Includes the normalized vertical offset used for direction. |
| Thumbs Down | `10000` | Other four folded; thumb tip is below wrist by more than 0.28 palm heights. | Shows **THUMBS DOWN**. | Includes the normalized vertical offset used for direction. |
| Pointing / Index Finger | `01000` | Only index extended. | Shows **POINTING / INDEX FINGER**. | Shows the actual finger states and rule match. |
| Three Fingers | `01110` | Index, middle, and ring extended; thumb and pinky folded. | Shows **THREE FINGERS**. | Shows pattern and per-finger reasons. |
| Four Fingers | `01111` | Four long fingers extended with thumb folded. | Shows **FOUR FINGERS**. | Shows pattern and per-finger reasons. |
| OK | `11111` | All states extended and thumb/index tip distance is under 0.32 palm widths. | Shows **OK**. | Displays tip distance relative to palm width and matching condition. |
| Rock | `01001` | Index and pinky extended; the other three folded. | Shows **ROCK**. | Shows pattern and matching rule. |

The processor judges the four long fingers using tip-to-wrist distance relative to the corresponding PIP-joint distance. Thumb extension compares thumb-tip and thumb-IP distance to the index MCP. This avoids fixed pixel sizes and is more tolerant of distance from the camera. Up/down uses the thumb's vertical displacement divided by palm height. OK uses thumb/index tip separation divided by palm width.

## 21 hand landmarks

MediaPipe numbers points consistently: **0** wrist; **1–4** thumb (CMC, MCP, IP, tip); **5–8** index (MCP, PIP, DIP, tip); **9–12** middle; **13–16** ring; **17–20** pinky. For each long finger the four points run from palm knuckle through PIP and DIP to fingertip. Each point has normalized `x`, `y`, and relative `z` values.

## Tests

No webcam is needed for the logic tests. From the project directory, with the environment active, run:

```powershell
python -m unittest discover -s tests -v
```

The tests cover the structured recognition result, common pattern mappings, OK's distance requirement, up/down geometry, landmark-count validation, measurement output, and the angle helper. They do not test camera hardware or MediaPipe model inference.

## Troubleshooting

- **Camera does not open:** close Teams/Zoom/other camera apps, check Windows Settings → Privacy & security → Camera, and try `CAMERA_INDEX = 1` in `config.py` if another device is the webcam.
- **Model download fails:** connect to the internet and rerun. Alternatively download Google's `hand_landmarker.task` asset from the URL in `modules/utils.py` and place it at the configured `MODEL_PATH`.
- **`mediapipe` cannot be installed:** use a supported 64-bit CPython release (recommended 3.10–3.12), recreate the virtual environment, then reinstall. Avoid mixing unrelated OpenCV/MediaPipe packages in a global Python installation.
- **No hand appears:** improve lighting, keep the full hand in frame, and show the palm clearly. Two-hand tracking uses more compute than one-hand tracking; set `MAX_HANDS = 1` if performance is low.
- **Gesture labels vary:** rule-based vision depends on camera angle, occlusion, hand anatomy, and landmark quality. Turn the palm toward the camera and hold the pose briefly.
- **Windows show separately/off-screen:** move and resize them manually; `config.py` contains default dimensions and the analysis-window horizontal offset.

## Limitations and future improvements

These geometric rules are interpretable, not guaranteed or 100% reliable. A side-on hand, crossed fingers, occlusion, or unusual rotation can make finger-state heuristics wrong. Up/down is relative to the image's vertical axis. Handedness can be affected by mirroring; the classifier does not rely on handedness. Try the provided rules first, then adjust thresholds in `landmark_processor.py` and `gesture_recognizer.py` for the camera and gesture style in use.

Possible improvements include temporal smoothing to reduce flicker, calibration settings, confidence-aware voting, a configurable gesture-rule file, and broader tests with recorded landmark samples.

## Configuration

Edit `config.py` to change the camera index, capture resolution, number of hands, model path, minimum detector/tracker confidence, mirror behavior, window sizes, and window spacing. The paths are relative to the project working directory; no absolute machine-specific path is embedded.
