## Архитектура проекта

Вебкамера (OpenCV)
      ↓
Детекция руки (MediaPipe Tasks API — HandLandmarker)
      ↓
21 точка координат пальцев + handedness
      ↓
Логика жестов (чистый Python)
      ↓
Действия на ПК (PyAutoGUI)


## Структура проекта

gesture_control/
├── main.py                # Точка входа
├── hand_tracker.py        # Обёртка над MediaPipe Tasks API
├── gesture_recognizer.py  # Логика жестов
├── controller.py          # Действия PyAutoGUI
├── config.py              # Настройки
├── hand_landmarker.task   # Модель MediaPipe (скачивается автоматически)
├── requirements.txt
├── README.md
├── CHANGES.md
└── CLAUDE.md


## Установка

```
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
# source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
python main.py
```

## Совместимость Python

MediaPipe 0.10.35 wheel: py3-none-win_amd64 → работает с Python 3.11 и 3.12.
