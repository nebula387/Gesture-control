import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from controller import MouseController
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    tracker = HandTracker()
    recognizer = GestureRecognizer()
    controller = MouseController(FRAME_WIDTH, FRAME_HEIGHT)

    prev_time = 0

    print("Запущено. ESC для выхода. Мышь в угол = аварийная остановка.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)   # Зеркало — так естественнее
        frame, landmarks, handedness = tracker.find_hands(frame)
        fingers = tracker.fingers_up(landmarks, handedness)
        gesture = recognizer.recognize(fingers)
        controller.execute(gesture, landmarks)

        # FPS счётчик
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time + 1e-9))
        prev_time = curr_time

        # Отладочная информация на экране
        cv2.putText(frame, f"FPS: {fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Fingers: {fingers}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
