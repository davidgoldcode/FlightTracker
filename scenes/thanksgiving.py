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

# fall colors
LEAF_COLORS = [
    (200, 80, 30),   # orange
    (180, 50, 20),   # red-orange
    (220, 150, 50),  # gold
    (150, 40, 20),   # dark red
    (180, 120, 40),  # brown-gold
]


class Leaf:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 70)
        self.y = random.uniform(-10, 0)
        self.speed = random.uniform(0.2, 0.4)
        self.drift = random.uniform(-0.3, 0.1)
        self.color = random.choice(LEAF_COLORS)
        self.wobble_phase = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.1, 0.2)


def get_thanksgiving_date(year):
    """Get 4th Thursday of November."""
    # find first day of november
    nov1 = date(year, 11, 1)
    # find first thursday (weekday 3)
    days_until_thursday = (3 - nov1.weekday()) % 7
    first_thursday = nov1.day + days_until_thursday
    # 4th thursday
    fourth_thursday = first_thursday + 21
    return date(year, 11, fourth_thursday)


class ThanksgivingScene(object):
    def __init__(self):
        super().__init__()
        self._leaves = [Leaf() for _ in range(15)]
        self._last_thanksgiving_pixels = []
        self._thanksgiving_phase = 0

    def _is_thanksgiving(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("thanksgiving", False):
                return False
        except (ImportError, NameError):
            return False
        today = date.today()
        return today == get_thanksgiving_date(today.year)

    def _draw_turkey(self, drawn_pixels, x, y):
        """Draw a simple turkey."""
        brown = (139, 90, 43)
        red = (200, 50, 50)
        orange = (255, 140, 0)
        yellow = (255, 200, 50)

        # tail feathers (fan shape)
        feather_colors = [red, orange, yellow, orange, red]
        for i, fc in enumerate(feather_colors):
            angle = math.radians(-60 + i * 30)
            for dist in range(4, 8):
                fx = int(x + math.cos(angle) * dist)
                fy = int(y - 3 + math.sin(angle) * dist * 0.5)
                if 0 <= fx < 64 and 0 <= fy < 32:
                    self.canvas.SetPixel(fx, fy, *fc)
                    drawn_pixels.append((fx, fy))

        # body
        body = [(0, 0), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1), (0, -1)]
        for dx, dy in body:
            px, py = x + dx, y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, *brown)
                drawn_pixels.append((px, py))

        # head (to the right)
        head = [(2, -1), (3, -1), (2, -2)]
        for dx, dy in head:
            px, py = x + dx, y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, *brown)
                drawn_pixels.append((px, py))

        # wattle (red)
        if 0 <= x + 3 < 64 and 0 <= y < 32:
            self.canvas.SetPixel(x + 3, y, *red)
            drawn_pixels.append((x + 3, y))

        # beak
        if 0 <= x + 4 < 64 and 0 <= y - 1 < 32:
            self.canvas.SetPixel(x + 4, y - 1, *orange)
            drawn_pixels.append((x + 4, y - 1))

    @Animator.KeyFrame.add(1)
    def thanksgiving(self, count):
        if len(self._data):
            if self._last_thanksgiving_pixels:
                for px, py in self._last_thanksgiving_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_thanksgiving_pixels = []
            return

        if not self._is_thanksgiving():
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        for px, py in self._last_thanksgiving_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._thanksgiving_phase += 0.08

        # warm autumn gradient background
        for y in range(32):
            for x in range(64):
                # warm orange/brown gradient
                intensity = 0.15 + 0.03 * math.sin(self._thanksgiving_phase + y * 0.15)
                r = int(180 * intensity)
                g = int(100 * intensity)
                b = int(50 * intensity)
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        # falling leaves
        for leaf in self._leaves:
            leaf.y += leaf.speed
            leaf.wobble_phase += leaf.wobble_speed
            leaf.x += leaf.drift + math.sin(leaf.wobble_phase) * 0.3

            if leaf.y > 35 or leaf.x < -5:
                leaf.reset()
                continue

            px, py = int(leaf.x), int(leaf.y)
            if 0 <= px < 64 and 0 <= py < 32:
                r, g, b = leaf.color
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))
                # make leaf 2 pixels
                if px + 1 < 64:
                    self.canvas.SetPixel(px + 1, py, r, g, b)
                    drawn_pixels.append((px + 1, py))

        # draw turkey
        self._draw_turkey(drawn_pixels, 50, 24)

        # "Give Thanks" text
        text = "Give Thanks"
        pulse = 0.7 + 0.3 * math.sin(self._thanksgiving_phase * 2)
        text_color = graphics.Color(int(220 * pulse), int(150 * pulse), int(50 * pulse))
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 12, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(6, 14):
                drawn_pixels.append((tx, ty))

        self._last_thanksgiving_pixels = drawn_pixels
