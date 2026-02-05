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

# chanukah dates (first night, varies by Hebrew calendar)
CHANUKAH_DATES = {
    2024: (12, 25),
    2025: (12, 14),
    2026: (12, 4),
    2027: (12, 24),
    2028: (12, 12),
    2029: (12, 2),
    2030: (12, 21),
    2031: (12, 11),
    2032: (11, 29),
    2033: (12, 18),
    2034: (12, 7),
    2035: (12, 27),
}


class Star:
    def __init__(self):
        self.x = random.randint(0, 63)
        self.y = random.randint(0, 10)
        self.brightness = random.uniform(0.3, 1.0)
        self.twinkle_speed = random.uniform(0.05, 0.15)
        self.phase = random.uniform(0, math.pi * 2)


class ChanukahScene(object):
    def __init__(self):
        super().__init__()
        self._chanukah_stars = [Star() for _ in range(15)]
        self._last_chanukah_pixels = []
        self._flame_phase = 0

    def _get_chanukah_night(self):
        """Return which night of Chanukah (1-8) or 0 if not Chanukah."""
        if DEMO_MODE:
            return 5

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
            return delta + 1
        return 0

    def _draw_menorah(self, drawn_pixels, night):
        """Draw a beautiful menorah with candles lit for the given night."""
        # colors
        gold = (200, 150, 50)
        blue = (80, 120, 255)
        white = (220, 220, 255)

        # menorah is centered, 50 pixels wide
        center_x = 32
        base_y = 28

        # draw ornate base
        for dx in range(-20, 21):
            self.canvas.SetPixel(center_x + dx, base_y, *gold)
            drawn_pixels.append((center_x + dx, base_y))
        for dx in range(-15, 16):
            self.canvas.SetPixel(center_x + dx, base_y - 1, *gold)
            drawn_pixels.append((center_x + dx, base_y - 1))

        # candle positions: 4 left, shamash center (raised), 4 right
        # positions relative to center_x
        candle_x_offsets = [-18, -13, -9, -5, 0, 5, 9, 13, 18]
        shamash_idx = 4

        # which candles to light (shamash always + night candles from right)
        lit_candles = {shamash_idx}  # shamash always lit
        # light from right to left: indices 8,7,6,5 then 3,2,1,0
        order = [8, 7, 6, 5, 3, 2, 1, 0]
        for i in range(min(night, 8)):
            lit_candles.add(order[i])

        # draw each candle position
        for idx, x_off in enumerate(candle_x_offsets):
            cx = center_x + x_off
            is_shamash = (idx == shamash_idx)

            # stem height and candle height
            if is_shamash:
                stem_top = base_y - 10
                candle_height = 5
            else:
                stem_top = base_y - 7
                candle_height = 4

            # draw stem (gold)
            for y in range(base_y - 1, stem_top, -1):
                self.canvas.SetPixel(cx, y, *gold)
                drawn_pixels.append((cx, y))

            # draw candle holder cup
            self.canvas.SetPixel(cx - 1, stem_top, *gold)
            self.canvas.SetPixel(cx + 1, stem_top, *gold)
            drawn_pixels.append((cx - 1, stem_top))
            drawn_pixels.append((cx + 1, stem_top))

            # draw candle (blue/white alternating)
            candle_color = blue if idx % 2 == 0 else white
            candle_top = stem_top - candle_height
            for y in range(stem_top - 1, candle_top, -1):
                self.canvas.SetPixel(cx, y, *candle_color)
                drawn_pixels.append((cx, y))

            # draw flame if lit
            if idx in lit_candles:
                flame_y = candle_top
                flicker = 0.6 + 0.4 * math.sin(self._flame_phase + idx * 0.7)

                # flame core (yellow-white)
                fr = int(255 * flicker)
                fg = int(220 * flicker)
                fb = int(100 * flicker)
                self.canvas.SetPixel(cx, flame_y, fr, fg, fb)
                drawn_pixels.append((cx, flame_y))

                # flame tip (orange glow)
                if flame_y - 1 >= 0:
                    self.canvas.SetPixel(cx, flame_y - 1, int(255 * flicker * 0.6), int(150 * flicker * 0.6), 0)
                    drawn_pixels.append((cx, flame_y - 1))

    @Animator.KeyFrame.add(1)
    def chanukah(self, count):
        if len(self._data):
            if self._last_chanukah_pixels:
                for px, py in self._last_chanukah_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_chanukah_pixels = []
            return

        night = self._get_chanukah_night()
        if night == 0:
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        # clear previous
        for px, py in self._last_chanukah_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)

        self._flame_phase += 0.15

        # draw twinkling stars in background
        for star in self._chanukah_stars:
            star.phase += star.twinkle_speed
            brightness = star.brightness * (0.5 + 0.5 * math.sin(star.phase))
            r = g = b = int(100 * brightness)
            # slight blue tint
            b = int(150 * brightness)
            if brightness > 0.3:
                self.canvas.SetPixel(star.x, star.y, r, g, b)
                drawn_pixels.append((star.x, star.y))

        # draw menorah
        self._draw_menorah(drawn_pixels, night)

        # "Night X" text at very top
        text = f"Night {night}"
        text_color = graphics.Color(100, 150, 255)
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 6, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(0, 8):
                drawn_pixels.append((tx, ty))

        self._last_chanukah_pixels = drawn_pixels
