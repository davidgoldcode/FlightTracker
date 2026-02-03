import math
import random
from datetime import datetime, date
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

# chanukah dates (approximate, varies by Hebrew calendar)
# format: (year, month, day) for first night
CHANUKAH_DATES = {
    2024: (12, 25),  # Dec 25, 2024
    2025: (12, 14),  # Dec 14, 2025
    2026: (12, 4),   # Dec 4, 2026
    2027: (12, 24),  # Dec 24, 2027
    2028: (12, 12),  # Dec 12, 2028
}


class Dreidel:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 50)
        self.y = random.uniform(22, 28)
        self.spin = random.uniform(0, math.pi * 2)
        self.spin_speed = random.uniform(0.2, 0.4)


class ChanukahScene(object):
    def __init__(self):
        super().__init__()
        self._dreidels = [Dreidel() for _ in range(2)]
        self._last_chanukah_pixels = []
        self._flame_phase = 0

    def _get_chanukah_night(self):
        """Return which night of Chanukah (1-8) or 0 if not Chanukah."""
        if DEMO_MODE:
            return 5  # demo shows 5 candles lit

        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("chanukah", False):
                return 0
        except (ImportError, NameError):
            return 0

        today = date.today()
        year = today.year

        if year not in CHANUKAH_DATES:
            return 0

        month, day = CHANUKAH_DATES[year]
        first_night = date(year, month, day)

        delta = (today - first_night).days
        if 0 <= delta < 8:
            return delta + 1  # night 1-8
        return 0

    def _draw_menorah(self, drawn_pixels, night):
        """Draw menorah with candles lit for the given night."""
        # menorah base (gold)
        base_x = 16
        base_y = 20

        # base structure
        gold = (200, 150, 50)

        # horizontal base
        for x in range(base_x, base_x + 32):
            self.canvas.SetPixel(x, base_y + 8, *gold)
            drawn_pixels.append((x, base_y + 8))

        # vertical supports for 9 candles (shamash in center, raised)
        candle_positions = []
        for i in range(9):
            cx = base_x + 2 + i * 3
            if i == 4:  # shamash (center, taller)
                cy = base_y - 2
                # taller stem
                for y in range(base_y + 8, cy, -1):
                    self.canvas.SetPixel(cx, y, *gold)
                    drawn_pixels.append((cx, y))
            else:
                cy = base_y
                # regular stem
                for y in range(base_y + 8, cy, -1):
                    self.canvas.SetPixel(cx, y, *gold)
                    drawn_pixels.append((cx, y))
            candle_positions.append((cx, cy, i == 4))

        # draw candles and flames
        # shamash is always lit, then candles right to left
        candles_to_light = []
        candles_to_light.append(4)  # shamash always
        # light from right to left (index 8, 7, 6, 5, then 3, 2, 1, 0)
        right_side = [8, 7, 6, 5]
        left_side = [3, 2, 1, 0]
        for i in range(night):
            if i < 4:
                candles_to_light.append(right_side[i])
            else:
                candles_to_light.append(left_side[i - 4])

        # draw all candles
        for idx, (cx, cy, is_shamash) in enumerate(candle_positions):
            # candle body (blue or white)
            candle_color = (100, 150, 255) if idx % 2 == 0 else (200, 200, 255)
            candle_height = 4 if is_shamash else 3
            for dy in range(candle_height):
                py = cy - dy
                if 0 <= py < 32:
                    self.canvas.SetPixel(cx, py, *candle_color)
                    drawn_pixels.append((cx, py))

            # flame if lit
            if idx in candles_to_light:
                flame_y = cy - candle_height
                # flickering flame
                flicker = 0.7 + 0.3 * math.sin(self._flame_phase + idx * 0.5)
                flame_r = int(255 * flicker)
                flame_g = int(200 * flicker)
                flame_b = int(50 * flicker)
                if 0 <= flame_y < 32:
                    self.canvas.SetPixel(cx, flame_y, flame_r, flame_g, flame_b)
                    drawn_pixels.append((cx, flame_y))
                # glow above
                if 0 <= flame_y - 1 < 32:
                    self.canvas.SetPixel(cx, flame_y - 1, flame_r // 2, flame_g // 2, 0)
                    drawn_pixels.append((cx, flame_y - 1))

    @Animator.KeyFrame.add(1)
    def chanukah(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_chanukah_pixels:
                for px, py in self._last_chanukah_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_chanukah_pixels = []
            return

        night = self._get_chanukah_night()
        if night == 0:
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_chanukah_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._flame_phase += 0.2

        # draw menorah
        self._draw_menorah(drawn_pixels, night)

        # "Night X" text at top
        text = f"Night {night}"
        text_color = graphics.Color(100, 150, 255)
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 7, text_color, text)
        for tx in range(x, min(64, x + len(text) * 5)):
            for ty in range(1, 9):
                drawn_pixels.append((tx, ty))

        # draw small dreidels
        for dreidel in self._dreidels:
            dreidel.spin += dreidel.spin_speed
            dx, dy = int(dreidel.x), int(dreidel.y)

            # simple dreidel: square with handle
            dreidel_color = (200, 150, 50)
            # body
            for ox in range(3):
                for oy in range(3):
                    px, py = dx + ox, dy + oy
                    if 0 <= px < 64 and 0 <= py < 32:
                        self.canvas.SetPixel(px, py, *dreidel_color)
                        drawn_pixels.append((px, py))
            # handle
            if 0 <= dy - 1 < 32:
                self.canvas.SetPixel(dx + 1, dy - 1, *dreidel_color)
                drawn_pixels.append((dx + 1, dy - 1))
            # point
            if 0 <= dy + 3 < 32:
                self.canvas.SetPixel(dx + 1, dy + 3, *dreidel_color)
                drawn_pixels.append((dx + 1, dy + 3))

        self._last_chanukah_pixels = drawn_pixels
