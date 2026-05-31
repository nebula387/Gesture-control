# Gesture Control — CLAUDE.md

## Задача проекта

Управление мышью компьютера с помощью жестов руки через веб-камеру.

## Стек

| Библиотека | Версия | Роль |
|---|---|---|
| MediaPipe | 0.10.35 | Детекция 21 точки руки (Tasks API) |
| OpenCV | 4.13.0 | Захват кадра с камеры |
| PyAutoGUI | 0.9.54 | Управление мышью/кликами |
| NumPy | 2.4.6 | Сглаживание координат |

## Совместимость Python

MediaPipe 0.10.35 на Windows имеет wheel-тег `py3-none-win_amd64` —
совместима с **Python 3.11 и 3.12** (более новые версии не тестировались).
Виртуальное окружение создано под Python 3.11.6.

## Архитектура

```
Камера (OpenCV)
    ↓
hand_tracker.py   — обёртка MediaPipe Tasks API, 21 landmark + handedness
    ↓
gesture_recognizer.py — словарь жестов (чистый Python)
    ↓
controller.py     — PyAutoGUI: move / click / drag / scroll
    ↓
config.py         — все числовые параметры
```

## Важные детали API

- `find_hands()` возвращает **3 значения**: `(frame, landmarks, handedness)`
- `handedness` — строка `'Left'` / `'Right'` / `None` из MediaPipe
- После `cv2.flip(frame, 1)` правая рука пользователя → MediaPipe говорит `'Left'`
- Буфер сглаживания — `collections.deque(maxlen=SMOOTHING_FACTOR)`, не list
- Модель `hand_landmarker.task` (~8 МБ) скачивается автоматически при первом запуске

## Запуск

```
.venv\Scripts\activate
python main.py
```

ESC — выход. Мышь в угол экрана — аварийная остановка (PyAutoGUI FAILSAFE).

## Жесты

| Жест | Пальцы [thumb, idx, mid, ring, pinky] | Действие |
|---|---|---|
| MOVE | `[0,1,0,0,0]` | Двигать курсор |
| LEFT_CLICK | `[0,1,1,0,0]` | Левый клик |
| RIGHT_CLICK | `[1,0,0,0,0]` | Правый клик |
| DRAG | `[0,0,0,0,0]` | Зажать кнопку мыши |
| RELEASE | `[1,1,1,1,1]` | Отпустить кнопку |
| SCROLL_UP | `[0,1,0,0,1]` | Прокрутить вверх |
| SCROLL_DOWN | `[1,1,0,0,1]` | Прокрутить вниз |

## Сессии работы с Claude

| Дата | Что сделано |
|---|---|
| 2026-05-31 | Аудит, исправления deque/thumb, переход на Tasks API, README (см. CHANGES.md) |
