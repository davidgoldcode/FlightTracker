import math
import random
from datetime import datetime
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

# tree shape (centered at x=32)
TREE_SHAPE = [
    # star on top (yellow)
    [(0, 0)],
    # tree tiers (green)
    [(-1, 2), (0, 2), (1, 2)],
    [(-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3)],
    [(-3, 4), (-2, 4), (-1, 4), (0, 4), (1, 4), (2, 4), (3, 4)],
    [(-2, 5), (-1, 5), (0, 5), (1, 5), (2, 5)],
    [(-3, 6), (-2, 6), (-1, 6), (0, 6), (1, 6), (2, 6), (3, 6)],
    [(-4, 7), (-3, 7), (-2, 7), (-1, 7), (0, 7), (1, 7), (2, 7), (3, 7), (4, 7)],
    [(-3, 8), (-2, 8), (-1, 8), (0, 8), (1, 8), (2, 8), (3, 8)],
    [(-4, 9), (-3, 9), (-2, 9), (-1, 9), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9)],
    [(-5, 10), (-4, 10), (-3, 10), (-2, 10), (-1, 10), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10)],
    # trunk (brown)
    [(0, 11), (0, 12)],
]

ORNAMENT_COLORS = [
    (255, 50, 50),   # red
    (50, 50, 255),   # blue
    (255, 200, 50),  # gold
    (255, 100, 200), # pink
]


class Snowflake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)
        self.speed = random.uniform(0.2, 0.5)
        self.drift = random.uniform(-0.1, 0.1)


class ChristmasScene(object):
    def __init__(self):
        super().__init__()
        self._christmas_snowflakes = [Snowflake() for _ in range(25)]
        self._last_christmas_pixels = []
        self._twinkle_phase = 0
        self._ornament_positions = [
            (-2, 3), (1, 4), (-3, 6), (2, 7), (-1, 8), (3, 9), (-4, 10), (0, 5)
        ]
        self._ornament_colors = [random.choice(ORNAMENT_COLORS) for _ in self._ornament_positions]

    def _is_christmas(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("christmas", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "12-25"

    @Animator.KeyFrame.add(1)
    def christmas(self, count):
        if len(self._data):
            if self._last_christmas_pixels:
                for px, py in self._last_christmas_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_christmas_pixels = []
            return

        if not self._is_christmas():
            return

        drawn_pixels = []

        for px, py in self._last_christmas_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._twinkle_phase += 0.15
        tree_x = 32
        tree_y = 8

        # draw falling snow
        for snow in self._christmas_snowflakes:
            snow.y += snow.speed
            snow.x += snow.drift

            if snow.y > 32:
                snow.reset()
                continue

            sx, sy = int(snow.x) % 64, int(snow.y)
            if 0 <= sy < 32:
                self.canvas.SetPixel(sx, sy, 200, 200, 255)
                drawn_pixels.append((sx, sy))

        # draw tree
        for tier_idx, tier in enumerate(TREE_SHAPE):
            for dx, dy in tier:
                px = tree_x + dx
                py = tree_y + dy

                if 0 <= px < 64 and 0 <= py < 32:
                    if tier_idx == 0:  # star
                        twinkle = 0.6 + 0.4 * math.sin(self._twinkle_phase * 2)
                        r, g, b = int(255 * twinkle), int(220 * twinkle), int(50 * twinkle)
                    elif tier_idx == len(TREE_SHAPE) - 1:  # trunk
                        r, g, b = 100, 60, 30
                    else:  # tree
                        r, g, b = 30, 120, 40
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw ornaments (twinkling)
        for i, (ox, oy) in enumerate(self._ornament_positions):
            px = tree_x + ox
            py = tree_y + oy
            if 0 <= px < 64 and 0 <= py < 32:
                twinkle = 0.5 + 0.5 * math.sin(self._twinkle_phase + i * 0.8)
                r, g, b = self._ornament_colors[i]
                r, g, b = int(r * twinkle), int(g * twinkle), int(b * twinkle)
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))

        # "Merry Christmas" text at bottom
        text = "Merry Christmas!"
        pulse = 0.7 + 0.3 * math.sin(self._twinkle_phase)
        text_color = graphics.Color(int(255 * pulse), int(50 * pulse), int(50 * pulse))
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 28, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(22, 30):
                drawn_pixels.append((tx, ty))

        self._last_christmas_pixels = drawn_pixels
