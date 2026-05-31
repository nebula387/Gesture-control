class GestureRecognizer:
    """
    Чистая логика без зависимостей.
    Принимает fingers_up список, возвращает название жеста.
    """

    GESTURES = {
        # [большой, указательный, средний, безымянный, мизинец]
        (0, 1, 0, 0, 0): "MOVE",          # Указательный — двигать мышь
        (0, 1, 1, 0, 0): "LEFT_CLICK",    # Два пальца — клик
        (1, 0, 0, 0, 0): "RIGHT_CLICK",   # Большой — правый клик
        (0, 0, 0, 0, 0): "DRAG",          # Кулак — зажать кнопку
        (1, 1, 1, 1, 1): "RELEASE",       # Открытая ладонь — отпустить
        (0, 1, 0, 0, 1): "SCROLL_UP",     # Рок-знак — скролл вверх
        (1, 1, 0, 0, 1): "SCROLL_DOWN",   # Три пальца — скролл вниз
    }

    def recognize(self, fingers):
        if not fingers:
            return "NO_HAND"
        return self.GESTURES.get(tuple(fingers), "UNKNOWN")
