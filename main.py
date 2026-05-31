import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from controller import MouseController
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TOGGLE_HOLD_SEC, ACTIVE_ZONE_MARGIN

# Жест-переключатель: большой палец + мизинец ("shaka")
# Удержать N секунд → PAUSED ↔ ACTIVE
_TOGGLE_FINGERS = [1, 0, 0, 0, 1]


def _draw_active_zone(frame):
    """Рисует рамку активной зоны — область, в которой движется рука."""
    h, w = frame.shape[:2]
    mx = int(w * ACTIVE_ZONE_MARGIN)
    my = int(h * ACTIVE_ZONE_MARGIN)
    cv2.rectangle(frame, (mx, my), (w - mx, h - my), (80, 80, 80), 1)


def _draw_status(frame, is_active, toggle_start, gesture, fingers, fps):
    h, w = frame.shape[:2]

    # Статус: ACTIVE зелёный, PAUSED красный
    status_text  = "ACTIVE" if is_active else "PAUSED"
    status_color = (0, 220, 0) if is_active else (0, 0, 220)
    cv2.putText(frame, status_text, (w - 130, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

    cv2.putText(frame, f"FPS: {fps}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if is_active:
        cv2.putText(frame, f"Gesture: {gesture}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Fingers: {fingers}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # Обратный отсчёт переключения
    if toggle_start is not None:
        held     = time.time() - toggle_start
        remain   = max(0.0, TOGGLE_HOLD_SEC - held)
        action   = "OFF" if is_active else "ON"
        pct      = held / TOGGLE_HOLD_SEC
        bar_w    = int(w * 0.6)
        filled   = int(bar_w * min(pct, 1.0))
        bar_x, bar_y = int(w * 0.2), h - 40
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 18), (50, 50, 50), -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled, bar_y + 18), (0, 200, 255), -1)
        cv2.putText(frame, f"Toggle {action}: {remain:.1f}s", (bar_x, bar_y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)

    if not is_active:
        cv2.putText(frame, "Hold shaka to activate", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    tracker    = HandTracker()
    recognizer = GestureRecognizer()
    controller = MouseController(FRAME_WIDTH, FRAME_HEIGHT)

    is_active    = False   # Запускается в режиме паузы
    toggle_start = None
    prev_time    = 0

    print("Запущено в режиме PAUSED.")
    print(f"Покажите shaka (большой+мизинец) и держите {TOGGLE_HOLD_SEC:.0f} сек — переключение.")
    print("ESC для выхода. Мышь в угол = аварийная остановка.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame, landmarks, handedness = tracker.find_hands(frame, draw=is_active)
        fingers = tracker.fingers_up(landmarks, handedness)
        gesture = recognizer.recognize(fingers)

        # --- Жест-переключатель ---
        if fingers == _TOGGLE_FINGERS:
            if toggle_start is None:
                toggle_start = time.time()
            elif time.time() - toggle_start >= TOGGLE_HOLD_SEC:
                is_active    = not is_active
                toggle_start = None
        else:
            toggle_start = None

        # --- Управление мышью только в активном режиме ---
        if is_active:
            controller.execute(gesture, landmarks)

        # --- Визуализация ---
        curr_time = time.time()
        fps       = int(1 / (curr_time - prev_time + 1e-9))
        prev_time = curr_time

        _draw_active_zone(frame)
        _draw_status(frame, is_active, toggle_start, gesture, fingers, fps)

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
