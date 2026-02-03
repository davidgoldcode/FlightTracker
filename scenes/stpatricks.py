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

# shamrock shape (3 leaves + stem)
SHAMROCK = [
    # left leaf
    (-3, 0), (-2, 0), (-2, -1), (-3, -1),
    # top leaf
    (0, -2), (0, -3), (-1, -2), (1, -2),
    # right leaf
    (2, 0), (3, 0), (2, -1), (3, -1),
    # center
    (0, 0), (-1, 0), (1, 0), (0, -1),
    # stem
    (0, 1), (0, 2), (0, 3),
]

GREEN_SHADES = [
    (30, 150, 50),
    (50, 180, 70),
    (40, 160, 60),
    (60, 200, 80),
]


class Shamrock:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-15, 0)
        self.speed = random.uniform(0.2, 0.5)
        self.drift = random.uniform(-0.15, 0.15)
        self.color = random.choice(GREEN_SHADES)
        self.size = random.choice([0.5, 0.7, 1.0])


class StPatricksScene(object):
    def __init__(self):
        super().__init__()
        self._shamrocks = [Shamrock() for _ in range(12)]
        self._last_stpatricks_pixels = []
        self._phase = 0

    def _is_st_patricks(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("st_patricks", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "03-17"

    @Animator.KeyFrame.add(1)
    def stpatricks(self, count):
        if len(self._data):
            if self._last_stpatricks_pixels:
                for px, py in self._last_stpatricks_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_stpatricks_pixels = []
            return

        if not self._is_st_patricks():
            return

        drawn_pixels = []

        for px, py in self._last_stpatricks_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._phase += 0.1

        # green gradient background (subtle)
        for y in range(32):
            intensity = 0.1 + 0.05 * math.sin(self._phase + y * 0.2)
            for x in range(64):
                r = int(10 * intensity)
                g = int(40 * intensity)
                b = int(15 * intensity)
                if r > 0 or g > 0:
                    self.canvas.SetPixel(x, y, r, g, b)
                    drawn_pixels.append((x, y))

        # draw falling shamrocks
        for shamrock in self._shamrocks:
            shamrock.y += shamrock.speed
            shamrock.x += shamrock.drift

            if shamrock.y > 35:
                shamrock.reset()
                continue

            r, g, b = shamrock.color
            for dx, dy in SHAMROCK:
                px = int(shamrock.x + dx * shamrock.size)
                py = int(shamrock.y + dy * shamrock.size)
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # "Happy St. Patrick's Day!" scrolling text
        text = "Happy St. Patrick's Day!"
        pulse = 0.7 + 0.3 * math.sin(self._phase * 2)
        text_color = graphics.Color(int(50 * pulse), int(200 * pulse), int(80 * pulse))
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 18, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(12, 20):
                drawn_pixels.append((tx, ty))

        # pot of gold at bottom right
        gold = (255, 200, 50)
        pot_x, pot_y = 52, 26
        # pot body
        for dx in range(8):
            for dy in range(4):
                px = pot_x + dx
                py = pot_y + dy
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, 80, 60, 40)
                    drawn_pixels.append((px, py))
        # gold coins
        for dx in range(1, 7):
            py = pot_y - 1
            px = pot_x + dx
            if 0 <= px < 64 and 0 <= py < 32:
                twinkle = 0.6 + 0.4 * math.sin(self._phase * 3 + dx)
                self.canvas.SetPixel(px, py, int(255 * twinkle), int(200 * twinkle), int(50 * twinkle))
                drawn_pixels.append((px, py))

        self._last_stpatricks_pixels = drawn_pixels
