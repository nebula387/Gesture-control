# Журнал изменений

## 2026-05-31 (сессия 2)

### [hand_tracker.py] Полная переработка на MediaPipe Tasks API

**Проблема:** `AttributeError: module 'mediapipe' has no attribute 'solutions'`
В MediaPipe 0.10.x API `mp.solutions` полностью удалён.
Пакет предоставляет только `mediapipe.tasks`.

**Исправление:** `hand_tracker.py` переписан на `mediapipe.tasks.python.vision.HandLandmarker`:
- Режим `RunningMode.VIDEO` — трекинг между кадрами, быстрее чем IMAGE
- Временна́я метка передаётся в `detect_for_video(image, ts_ms)` (монотонная, мс)
- Отрисовка скелета реализована вручную через cv2 (HAND_CONNECTIONS задан явно)
- Handedness: `result.handedness[0][0].category_name` → 'Left'/'Right'
- Возврат: `(frame, landmarks, handedness)` — интерфейс не изменился

**Модель:** `hand_landmarker.task` (~7.8 МБ) скачивается автоматически
при первом запуске (или можно скачать вручную заранее).

**Файл:** `hand_tracker.py`.

---

## 2026-05-31 (сессия 1)

### Анализ совместимости MediaPipe

**Вопрос:** MediaPipe устарела, нужна версия Python < 3.11?

**Ответ:** НЕТ. MediaPipe 0.10.35 на Windows имеет wheel-тег `py3-none-win_amd64`
(Python-version agnostic) и работает с Python 3.11 и 3.12. Миграция на другую
библиотеку не требуется.

---

### [controller.py] Буфер сглаживания: list → deque

**Проблема:** `smooth_x` и `smooth_y` были обычными списками. Удаление первого
элемента `pop(0)` на каждом кадре — операция O(n).

**Исправление:** Заменены на `collections.deque(maxlen=SMOOTHING_FACTOR)`.
Автоматически ограничивает размер, `append` — O(1).

**Файл:** `controller.py`, метод `__init__` и `_smooth`.

---

### [hand_tracker.py + main.py] Улучшение определения большого пальца

**Проблема:** Старая логика сравнивала THUMB_TIP vs соседний сустав (индекс 3).
Работало только для правой руки в зеркале.

**Исправление:**
- `find_hands()` возвращает 3 значения: `(frame, landmarks, handedness)`
- `fingers_up()` принимает `handedness`, сравнивает THUMB_TIP с THUMB_MCP (индекс 2)
- После `cv2.flip` правая рука → MediaPipe говорит `'Left'` → tip_x > mcp_x при поднятом пальце
- `main.py` обновлён для распаковки 3 значений

**Файлы:** `hand_tracker.py`, `main.py`.

---

### [requirements.txt] Создан файл зависимостей

Файл отсутствовал в проекте. Создан с минимальными версиями пакетов.
