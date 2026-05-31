import pyautogui
import time
import numpy as np
from collections import deque
from config import SMOOTHING_FACTOR, GESTURE_COOLDOWN, ACTIVE_ZONE_MARGIN

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
        """Координаты кадра → координаты экрана с учётом активной зоны.

        ACTIVE_ZONE_MARGIN обрезает края кадра: центральная часть маппится
        на весь экран, что повышает чувствительность при работе с расстояния.
        0.0 = весь кадр, 0.20 = центральные 60%.
        """
        mx = int(self.frame_w * ACTIVE_ZONE_MARGIN)
        my = int(self.frame_h * ACTIVE_ZONE_MARGIN)
        active_w = self.frame_w - 2 * mx
        active_h = self.frame_h - 2 * my
        sx = int((x - mx) * self.screen_w / active_w)
        sy = int((y - my) * self.screen_h / active_h)
        sx = max(0, min(self.screen_w - 1, sx))
        sy = max(0, min(self.screen_h - 1, sy))
        return sx, sy

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
