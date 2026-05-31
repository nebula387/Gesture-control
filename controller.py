import pyautogui
import time
import numpy as np
from collections import deque
from config import SMOOTHING_FACTOR, GESTURE_COOLDOWN

pyautogui.FAILSAFE = True   # Мышь в угол = аварийная остановка
pyautogui.PAUSE = 0.01      # Минимальная задержка между командами

class MouseController:
    def __init__(self, frame_w, frame_h):
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.screen_w, self.screen_h = pyautogui.size()

        self.prev_x, self.prev_y = 0, 0
        self.last_gesture_time = 0
        self.is_dragging = False

        # deque с maxlen вместо list+pop(0) — O(1) вместо O(n)
        self.smooth_x = deque(maxlen=SMOOTHING_FACTOR)
        self.smooth_y = deque(maxlen=SMOOTHING_FACTOR)

    def _smooth(self, x, y):
        """Скользящее среднее для плавного движения."""
        self.smooth_x.append(x)
        self.smooth_y.append(y)
        return int(np.mean(self.smooth_x)), int(np.mean(self.smooth_y))

    def _map_to_screen(self, x, y):
        """Координаты кадра → координаты экрана."""
        screen_x = int(x * self.screen_w / self.frame_w)
        screen_y = int(y * self.screen_h / self.frame_h)
        return screen_x, screen_y

    def _cooldown_ok(self):
        """Защита от случайных повторных жестов."""
        if time.time() - self.last_gesture_time > GESTURE_COOLDOWN:
            self.last_gesture_time = time.time()
            return True
        return False

    def execute(self, gesture, landmarks):
        if not landmarks:
            return

        # Используем кончик указательного пальца как курсор
        fx, fy = landmarks[8]
        sx, sy = self._map_to_screen(fx, fy)
        sx, sy = self._smooth(sx, sy)

        if gesture == "MOVE":
            pyautogui.moveTo(sx, sy)

        elif gesture == "LEFT_CLICK" and self._cooldown_ok():
            pyautogui.click(sx, sy)

        elif gesture == "RIGHT_CLICK" and self._cooldown_ok():
            pyautogui.rightClick(sx, sy)

        elif gesture == "DRAG":
            if not self.is_dragging:
                pyautogui.mouseDown()
                self.is_dragging = True
            pyautogui.moveTo(sx, sy)

        elif gesture == "RELEASE":
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False

        elif gesture == "SCROLL_UP" and self._cooldown_ok():
            pyautogui.scroll(3)

        elif gesture == "SCROLL_DOWN" and self._cooldown_ok():
            pyautogui.scroll(-3)
