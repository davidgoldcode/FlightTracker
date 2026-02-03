import math
import random
from datetime import datetime, date
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


def _is_demo_mode():
    try:
        from config import HOLIDAYS
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()

# easter dates (calculated using anonymous gregorian algorithm)
EASTER_DATES = {
    2024: (3, 31),
    2025: (4, 20),
    2026: (4, 5),
    2027: (3, 28),
    2028: (4, 16),
    2029: (4, 1),
}

PASTEL_COLORS = [
    (255, 182, 193),  # pink
    (173, 216, 230),  # light blue
    (144, 238, 144),  # light green
    (255, 255, 150),  # light yellow
    (221, 160, 221),  # plum
    (255, 218, 185),  # peach
]

# egg shape (oval)
EGG_SHAPE = [
    (0, -2),
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (0, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1),
    (0, 2),
]


class Egg:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)
        self.speed = random.uniform(0.15, 0.35)
        self.color = random.choice(PASTEL_COLORS)
        self.pattern_color = random.choice(PASTEL_COLORS)
        self.pattern_type = random.randint(0, 2)


class EasterScene(object):
    def __init__(self):
        super().__init__()
        self._eggs = [Egg() for _ in range(8)]
        self._last_easter_pixels = []
        self._phase = 0
        self._bunny_hop = 0

    def _is_easter(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("easter", False):
                return False
        except (ImportError, NameError):
            return False
        today = date.today()
        year = today.year
        if year not in EASTER_DATES:
            return False
        month, day = EASTER_DATES[year]
        return today == date(year, month, day)

    def _draw_bunny(self, drawn_pixels, x, y):
        """Draw a simple bunny silhouette."""
        white = (240, 240, 240)
        pink = (255, 180, 180)

        # hop animation
        hop_offset = int(abs(math.sin(self._bunny_hop)) * 2)
        y -= hop_offset

        # body (oval)
        body = [(0, 0), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1), (0, 2)]
        for dx, dy in body:
            px, py = x + dx, y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, *white)
                drawn_pixels.append((px, py))

        # head
        head = [(0, -1), (-1, -1), (1, -1), (0, -2)]
        for dx, dy in head:
            px, py = x + dx, y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, *white)
                drawn_pixels.append((px, py))

        # ears
        ears = [(-1, -3), (-1, -4), (1, -3), (1, -4)]
        for dx, dy in ears:
            px, py = x + dx, y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, *white)
                drawn_pixels.append((px, py))

        # inner ears (pink)
        if 0 <= x - 1 < 64 and 0 <= y - 4 < 32:
            self.canvas.SetPixel(x - 1, y - 4, *pink)
        if 0 <= x + 1 < 64 and 0 <= y - 4 < 32:
            self.canvas.SetPixel(x + 1, y - 4, *pink)

        # tail
        if 0 <= x + 2 < 64 and 0 <= y + 1 < 32:
            self.canvas.SetPixel(x + 2, y + 1, *white)
            drawn_pixels.append((x + 2, y + 1))

    @Animator.KeyFrame.add(1)
    def easter(self, count):
        if len(self._data):
            if self._last_easter_pixels:
                for px, py in self._last_easter_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_easter_pixels = []
            return

        if not self._is_easter():
            return

        drawn_pixels = []

        for px, py in self._last_easter_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._phase += 0.1
        self._bunny_hop += 0.15

        # pastel gradient background
        for y in range(32):
            for x in range(64):
                intensity = 0.15 + 0.05 * math.sin(self._phase + y * 0.1)
                r = int(255 * intensity * 0.4)
                g = int(230 * intensity * 0.4)
                b = int(200 * intensity * 0.4)
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        # draw falling eggs
        for egg in self._eggs:
            egg.y += egg.speed

            if egg.y > 35:
                egg.reset()
                continue

            r, g, b = egg.color
            for dx, dy in EGG_SHAPE:
                px = int(egg.x + dx)
                py = int(egg.y + dy)
                if 0 <= px < 64 and 0 <= py < 32:
                    # add pattern stripe
                    if egg.pattern_type == 0 and dy == 0:
                        pr, pg, pb = egg.pattern_color
                        self.canvas.SetPixel(px, py, pr, pg, pb)
                    elif egg.pattern_type == 1 and dy in [-1, 1]:
                        pr, pg, pb = egg.pattern_color
                        self.canvas.SetPixel(px, py, pr, pg, pb)
                    else:
                        self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw bunny
        self._draw_bunny(drawn_pixels, 10, 24)

        # "Happy Easter!" text
        text = "Happy Easter!"
        pulse = 0.7 + 0.3 * math.sin(self._phase * 2)
        text_color = graphics.Color(int(200 * pulse), int(150 * pulse), int(200 * pulse))
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 10, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(4, 12):
                drawn_pixels.append((tx, ty))

        self._last_easter_pixels = drawn_pixels
