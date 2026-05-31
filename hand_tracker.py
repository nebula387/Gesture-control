import cv2
import time
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

HAND_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 4),
    (5, 6), (6, 7), (7, 8),
    (9, 10), (10, 11), (11, 12),
    (13, 14), (14, 15), (15, 16),
    (17, 18), (18, 19), (19, 20),
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17),
])


def _download_model():
    print("Скачиваю модель hand_landmarker.task (~8 МБ)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Модель загружена.")


class HandTracker:
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    INDEX_MCP = 5
    MIDDLE_MCP = 9
    RING_MCP = 13
    PINKY_MCP = 17

    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            _download_model()

        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_ts = -1

    def find_hands(self, frame, draw=True):
        """Возвращает (frame, landmarks, handedness). handedness: 'Left'/'Right'/None."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        ts = int(time.time() * 1000)
        if ts <= self._last_ts:
            ts = self._last_ts + 1
        self._last_ts = ts

        result = self._landmarker.detect_for_video(mp_image, ts)

        landmarks = []
        handedness = None

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            if result.handedness:
                handedness = result.handedness[0][0].category_name
            h, w, _ = frame.shape
            for lm in hand:
                landmarks.append((int(lm.x * w), int(lm.y * h)))
            if draw:
                self._draw(frame, landmarks)

        return frame, landmarks, handedness

    def _draw(self, frame, pts):
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (0, 128, 255), -1)

    def fingers_up(self, landmarks, handedness=None):
        """
        Возвращает [большой, указ, средний, безымянный, мизинец], 1=поднят, 0=согнут.
        handedness — строка из find_hands (MediaPipe на зеркальном кадре).
        После cv2.flip правая рука определяется как 'Left' → большой палец справа.
        """
        if not landmarks:
            return []

        fingers = []

        tip_x = landmarks[self.THUMB_TIP][0]
        mcp_x = landmarks[2][0]  # THUMB_MCP
        if handedness == "Left":   # правая рука пользователя в зеркале
            fingers.append(1 if tip_x > mcp_x else 0)
        else:                      # левая рука пользователя в зеркале
            fingers.append(1 if tip_x < mcp_x else 0)

        tips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        mcps = [self.INDEX_MCP, self.MIDDLE_MCP, self.RING_MCP, self.PINKY_MCP]
        for tip, mcp in zip(tips, mcps):
            fingers.append(1 if landmarks[tip][1] < landmarks[mcp][1] else 0)

        return fingers
