import random
import math
from utilities.animator import Animator
from utilities.quiethours import should_display_be_dim
from setup import frames


def _is_demo_mode():
    try:
        from config import ZONE_HOME
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()

# moon pixel offsets for a 7-pixel diameter circle with crescent shadow
MOON_PIXELS = [
    # full circle
    (-1, -3), (0, -3), (1, -3),
    (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
    (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (3, -1),
    (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0),
    (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1),
    (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
    (-1, 3), (0, 3), (1, 3),
]

# crescent shadow (right side, makes it look like a waning crescent)
SHADOW_PIXELS = {
    (2, -2), (2, -1), (3, -1),
    (2, 0), (3, 0),
    (2, 1), (3, 1),
    (2, 2),
}

MOON_COLOR = (230, 220, 180)       # warm white
SHADOW_COLOR = (40, 35, 25)        # dark but not black (subtle crater shadow)

# star settings
NUM_STARS = 30
STAR_COLORS = [
    (180, 180, 200),  # cool white
    (140, 140, 160),  # dim
    (100, 100, 120),  # very dim
]

# sky gradient (top to bottom)
SKY_TOP = (5, 5, 20)       # dark navy
SKY_BOTTOM = (15, 10, 30)  # slightly purple horizon


class NightStar:
    def __init__(self):
        self.x = random.randint(0, 63)
        self.y = random.randint(0, 31)
        self.color = random.choice(STAR_COLORS)
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.02, 0.08)


class MoonriseScene(object):
    def __init__(self):
        super().__init__()
        self._moon_phase = 0.0
        self._moon_stars = [NightStar() for _ in range(NUM_STARS)]
        self._last_moon_pixels = []

    def _get_moon_position(self):
        """Moon arcs slowly across the sky. Full cycle ~10 minutes."""
        t = self._moon_phase
        # arc from lower-left to upper-center to lower-right
        x = 8 + int(t * 48)  # x: 8 to 56
        # parabolic arc peaking at center
        normalized = (t - 0.5) * 2  # -1 to 1
        y = 20 - int((1 - normalized * normalized) * 16)  # peaks at y=4
        return x, y

    @Animator.KeyFrame.add(2)
    def moonrise(self, count):
        if len(self._data):
            if self._last_moon_pixels:
                for px, py in self._last_moon_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_moon_pixels = []
            return

        # only show during quiet hours or demo mode
        if not DEMO_MODE and not should_display_be_dim():
            if self._last_moon_pixels:
                for px, py in self._last_moon_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_moon_pixels = []
            return

        # quiet-hours ambient cycling
        if not self._register_quiet_ambient('moonrise'):
            if self._last_moon_pixels:
                for px, py in self._last_moon_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_moon_pixels = []
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_moon_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)
        self.clear_date_region(drawn_pixels)

        # advance moon position (very slow arc)
        self._moon_phase += 0.0003
        if self._moon_phase > 1.0:
            self._moon_phase = 0.0

        # draw sky gradient (subtle dark background)
        for y in range(11, 32):
            t = (y - 11) / 21.0
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            for x in range(64):
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        # draw twinkling stars
        moon_x, moon_y = self._get_moon_position()
        for star in self._moon_stars:
            star.phase += star.speed
            twinkle = (math.sin(star.phase) + 1) / 2
            if twinkle < 0.3:
                continue

            # don't draw stars near the moon
            dist = math.sqrt((star.x - moon_x) ** 2 + (star.y - moon_y) ** 2)
            if dist < 6:
                continue

            r, g, b = star.color
            factor = 0.3 + 0.7 * twinkle
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            if 0 <= star.x < 64 and 0 <= star.y < 32:
                self.canvas.SetPixel(star.x, star.y, r, g, b)
                drawn_pixels.append((star.x, star.y))

        # draw moon
        for dx, dy in MOON_PIXELS:
            px = moon_x + dx
            py = moon_y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                if (dx, dy) in SHADOW_PIXELS:
                    r, g, b = SHADOW_COLOR
                else:
                    r, g, b = MOON_COLOR
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))

        # subtle moonlight glow (halo around moon)
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                dist = math.sqrt(dx * dx + dy * dy)
                if 3.5 < dist <= 5:
                    px = moon_x + dx
                    py = moon_y + dy
                    if 0 <= px < 64 and 0 <= py < 32:
                        glow = (1 - (dist - 3.5) / 1.5) * 0.3
                        r = int(200 * glow)
                        g = int(190 * glow)
                        b = int(150 * glow)
                        if r > 0:
                            self.canvas.SetPixel(px, py, r, g, b)
                            drawn_pixels.append((px, py))

        self._last_moon_pixels = drawn_pixels
