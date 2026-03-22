from settings import SW, SH


class Camera:
    """Горизонтальная прокрутка: следит за игроком."""

    def __init__(self, level_width: int):
        self.offset_x   = 0
        self.level_w    = level_width
        self.max_offset = max(0, level_width - SW)

    def update(self, target_rect):
        # центрируем цель на 1/3 экрана от левого края
        desired = target_rect.centerx - SW // 3
        self.offset_x = max(0, min(desired, self.max_offset))

    def apply(self, rect):
        """Вернуть rect смещённый для рисования на экране."""
        return rect.move(-self.offset_x, 0)

    def apply_pos(self, x, y):
        return x - self.offset_x, y
