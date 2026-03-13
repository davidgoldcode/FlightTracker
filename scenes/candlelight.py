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

# candle positions across the display (x, base_y, height)
CANDLES = [
    (8, 28, 6),
    (20, 29, 5),
    (32, 27, 7),
    (44, 29, 5),
    (56, 28, 6),
]

# warm candle colors
CANDLE_BODY = (180, 170, 140)  # cream/wax
CANDLE_WICK = (60, 40, 20)

# flame color layers (inner to outer)
FLAME_COLORS = [
    (255, 255, 200),  # white-yellow core
    (255, 220, 100),  # bright yellow
    (255, 160, 40),   # orange
    (200, 80, 10),    # dark orange glow
]

# warm ambient glow on nearby surfaces
GLOW_COLOR = (40, 20, 5)


class Candle:
    def __init__(self, x, base_y, height):
        self.x = x
        self.base_y = base_y
        self.height = height
        self.phase = random.uniform(0, 2 * math.pi)
        self.flicker_speed = random.uniform(0.08, 0.15)
        self.sway = 0.0
        self.sway_speed = random.uniform(0.03, 0.06)


class CandlelightScene(object):
    def __init__(self):
        super().__init__()
        self._candles = [Candle(x, y, h) for x, y, h in CANDLES]
        self._last_candle_pixels = []

    def _draw_flame(self, drawn_pixels, cx, tip_y, brightness, sway_offset):
        """Draw a flickering flame at the given position."""
        # flame is 3 pixels wide, 3-4 tall depending on flicker
        flame_height = 3 + int(brightness * 1.5)
        sway = int(sway_offset)

        for dy in range(flame_height):
            fy = tip_y - dy
            if not (0 <= fy < 32):
                continue

            # flame narrows toward the top
            if dy < 2:
                width = 1
            elif dy < flame_height - 1:
                width = 2
            else:
                width = 1

            # pick color based on height in flame
            color_idx = min(dy, len(FLAME_COLORS) - 1)
            r, g, b = FLAME_COLORS[color_idx]

            # apply brightness variation
            r = int(r * (0.6 + 0.4 * brightness))
            g = int(g * (0.6 + 0.4 * brightness))
            b = int(b * (0.6 + 0.4 * brightness))

            for dx in range(-width // 2, width // 2 + 1):
                px = cx + dx + sway
                if 0 <= px < 64:
                    self.canvas.SetPixel(px, fy, r, g, b)
                    drawn_pixels.append((px, fy))

    def _draw_glow(self, drawn_pixels, cx, base_y, brightness):
        """Draw subtle warm glow around candle base."""
        glow_radius = 4
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-2, 3):
                px = cx + dx
                py = base_y + dy
                if 0 <= px < 64 and 0 <= py < 32:
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= glow_radius:
                        factor = (1 - dist / glow_radius) * brightness * 0.5
                        r = int(GLOW_COLOR[0] * factor)
                        g = int(GLOW_COLOR[1] * factor)
                        b = int(GLOW_COLOR[2] * factor)
                        if r > 0 or g > 0:
                            self.canvas.SetPixel(px, py, r, g, b)
                            drawn_pixels.append((px, py))

    @Animator.KeyFrame.add(2)
    def candlelight(self, count):
        if len(self._data):
            if self._last_candle_pixels:
                for px, py in self._last_candle_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_candle_pixels = []
            return

        # only show during quiet hours or demo mode
        if not DEMO_MODE and not should_display_be_dim():
            return

        # quiet-hours ambient cycling
        if not self._register_quiet_ambient('candlelight'):
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_candle_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)
        self.clear_date_region(drawn_pixels)

        for candle in self._candles:
            candle.phase += candle.flicker_speed
            candle.sway += candle.sway_speed

            # flicker brightness (gentle, not erratic)
            brightness = 0.6 + 0.4 * ((math.sin(candle.phase) + 1) / 2)
            # occasional deeper flicker
            if random.random() < 0.02:
                brightness *= 0.5

            sway_offset = math.sin(candle.sway) * 0.8

            # draw candle body
            for dy in range(candle.height):
                py = candle.base_y - dy
                if 0 <= py < 32:
                    r, g, b = CANDLE_BODY
                    self.canvas.SetPixel(candle.x, py, r, g, b)
                    drawn_pixels.append((candle.x, py))
                    # wider base
                    if dy < candle.height // 2:
                        for dx in [-1, 1]:
                            px = candle.x + dx
                            if 0 <= px < 64:
                                self.canvas.SetPixel(px, py, r // 2, g // 2, b // 2)
                                drawn_pixels.append((px, py))

            # draw wick
            wick_y = candle.base_y - candle.height
            if 0 <= wick_y < 32:
                r, g, b = CANDLE_WICK
                self.canvas.SetPixel(candle.x, wick_y, r, g, b)
                drawn_pixels.append((candle.x, wick_y))

            # draw flame above wick
            flame_tip_y = wick_y - 1
            self._draw_flame(drawn_pixels, candle.x, flame_tip_y, brightness, sway_offset)

            # draw glow
            self._draw_glow(drawn_pixels, candle.x, candle.base_y, brightness)

        self._last_candle_pixels = drawn_pixels
