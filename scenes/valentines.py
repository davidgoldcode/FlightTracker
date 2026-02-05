import math
import random
from datetime import datetime
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


def _is_demo_mode():
    """Check if running in test/demo mode."""
    try:
        from config import HOLIDAYS
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()

# heart colors
HEART_COLORS = [
    (255, 50, 80),    # red
    (255, 100, 150),  # pink
    (255, 150, 180),  # light pink
    (200, 50, 100),   # dark pink
]


class Heart:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-15, -3)
        self.speed = random.uniform(0.3, 0.7)
        self.size = random.choice([1, 2])  # small or medium
        self.color = random.choice(HEART_COLORS)
        self.drift = random.uniform(-0.1, 0.1)

    def get_pixels(self):
        """Return list of (dx, dy) offsets for this heart size."""
        if self.size == 1:
            # tiny 3x3 heart
            return [
                (0, 0), (2, 0),
                (0, 1), (1, 1), (2, 1),
                (1, 2),
            ]
        else:
            # small 5x4 heart
            return [
                (1, 0), (2, 0), (4, 0), (5, 0),
                (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
                (2, 3), (3, 3), (4, 3),
                (3, 4),
            ]


class ValentinesScene(object):
    def __init__(self):
        super().__init__()
        self._hearts = [Heart() for _ in range(20)]
        self._last_valentines_pixels = []
        self._valentines_scroll_x = 64
        self._pulse_phase = 0

    def _is_valentines_day(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("valentines", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "02-14"

    @Animator.KeyFrame.add(1)
    def valentines(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_valentines_pixels:
                for px, py in self._last_valentines_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_valentines_pixels = []
            return

        if not self._is_valentines_day():
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        # clear previous
        for px, py in self._last_valentines_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._pulse_phase += 0.15

        # draw falling hearts
        for heart in self._hearts:
            heart.y += heart.speed
            heart.x += heart.drift

            if heart.y > 32:
                heart.reset()
                continue

            r, g, b = heart.color
            for dx, dy in heart.get_pixels():
                px = int(heart.x + dx) % 64
                py = int(heart.y + dy)
                if 0 <= py < 32:
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw scrolling message
        message = "Happy Valentine's Day!"
        pulse = 0.7 + 0.3 * math.sin(self._pulse_phase)
        text_color = graphics.Color(
            int(255 * pulse),
            int(100 * pulse),
            int(150 * pulse)
        )
        graphics.DrawText(
            self.canvas,
            fonts.extrasmall,
            int(self._valentines_scroll_x),
            18,
            text_color,
            message
        )

        # track text pixels
        for x in range(int(self._valentines_scroll_x), min(64, int(self._valentines_scroll_x) + len(message) * 5)):
            if 0 <= x < 64:
                for y in range(12, 20):
                    drawn_pixels.append((x, y))

        self._valentines_scroll_x -= 0.5
        if self._valentines_scroll_x < -len(message) * 5:
            self._valentines_scroll_x = 64

        self._last_valentines_pixels = drawn_pixels
