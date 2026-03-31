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

# single centered candle
CANDLE_X = 32
CANDLE_BASE_Y = 30
CANDLE_HEIGHT = 10

# candle body color
CANDLE_BODY = (160, 150, 120)
CANDLE_BODY_DIM = (100, 90, 70)
CANDLE_WICK = (50, 35, 15)

# flame color gradient (bottom to tip)
FLAME_GRADIENT = [
    (200, 80, 10),    # dark orange base
    (255, 140, 20),   # orange
    (255, 190, 50),   # yellow-orange
    (255, 220, 100),  # bright yellow
    (255, 245, 180),  # white-yellow core
    (255, 255, 220),  # near-white tip
]

# warm glow color
GLOW_WARM = (50, 25, 5)


class CandlelightScene(object):
    def __init__(self):
        super().__init__()
        self._candle_phase = random.uniform(0, 2 * math.pi)
        self._candle_sway_phase = random.uniform(0, 2 * math.pi)
        self._last_candle_pixels = []

    @Animator.KeyFrame.add(1)
    def candlelight(self, count):
        if len(self._data):
            if self._last_candle_pixels:
                for px, py in self._last_candle_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_candle_pixels = []
            return

        # only show during quiet hours or demo mode
        if not DEMO_MODE and not should_display_be_dim():
            if self._last_candle_pixels:
                for px, py in self._last_candle_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_candle_pixels = []
            return

        # quiet-hours ambient cycling
        if not self._register_quiet_ambient('candlelight'):
            if self._last_candle_pixels:
                for px, py in self._last_candle_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_candle_pixels = []
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_candle_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)
        self.clear_date_region(drawn_pixels)

        # advance animation
        self._candle_phase += 0.08
        self._candle_sway_phase += 0.03

        # gentle brightness variation
        brightness = 0.7 + 0.3 * ((math.sin(self._candle_phase) + 1) / 2)
        # occasional subtle dim
        if random.random() < 0.01:
            brightness *= 0.6
        sway = math.sin(self._candle_sway_phase) * 1.2

        # draw warm ambient glow (large soft circle behind candle)
        glow_cx = CANDLE_X
        glow_cy = CANDLE_BASE_Y - CANDLE_HEIGHT - 2
        glow_radius = 18
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-glow_radius, glow_radius + 1):
                px = glow_cx + dx
                py = glow_cy + dy
                if not (0 <= px < 64 and 0 <= py < 32):
                    continue
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > glow_radius:
                    continue
                factor = (1 - dist / glow_radius) ** 2 * brightness * 0.4
                r = int(GLOW_WARM[0] * factor)
                g = int(GLOW_WARM[1] * factor)
                b = int(GLOW_WARM[2] * factor)
                if r > 0 or g > 0:
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw candle body (3px wide, tapers at top)
        for dy in range(CANDLE_HEIGHT):
            py = CANDLE_BASE_Y - dy
            if not (0 <= py < 32):
                continue
            # wider at base, narrower at top
            if dy < CANDLE_HEIGHT * 0.4:
                half_width = 2
            elif dy < CANDLE_HEIGHT * 0.7:
                half_width = 1
            else:
                half_width = 1
            for dx in range(-half_width, half_width + 1):
                px = CANDLE_X + dx
                if 0 <= px < 64:
                    if dx == 0:
                        r, g, b = CANDLE_BODY
                    else:
                        r, g, b = CANDLE_BODY_DIM
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw wick
        wick_y = CANDLE_BASE_Y - CANDLE_HEIGHT
        if 0 <= wick_y < 32:
            self.canvas.SetPixel(CANDLE_X, wick_y, *CANDLE_WICK)
            drawn_pixels.append((CANDLE_X, wick_y))

        # draw flame (larger, more detailed)
        flame_base_y = wick_y - 1
        flame_height = 6 + int(brightness * 2)
        sway_int = int(sway)

        for dy in range(flame_height):
            fy = flame_base_y - dy
            if not (0 <= fy < 32):
                continue

            # flame width narrows toward tip
            progress = dy / flame_height  # 0 at base, 1 at tip
            if progress < 0.3:
                half_w = 2
            elif progress < 0.6:
                half_w = 1
            else:
                half_w = 0

            # pick color from gradient
            color_idx = int(progress * (len(FLAME_GRADIENT) - 1))
            color_idx = max(0, min(len(FLAME_GRADIENT) - 1, color_idx))
            r, g, b = FLAME_GRADIENT[color_idx]

            # apply brightness
            r = int(r * (0.5 + 0.5 * brightness))
            g = int(g * (0.5 + 0.5 * brightness))
            b = int(b * (0.5 + 0.5 * brightness))

            # sway increases toward tip
            tip_sway = int(sway * progress)

            for dx in range(-half_w, half_w + 1):
                px = CANDLE_X + dx + tip_sway
                if 0 <= px < 64:
                    # edges are dimmer
                    if dx != 0 and half_w > 0:
                        r2 = r * 2 // 3
                        g2 = g * 2 // 3
                        b2 = b * 2 // 3
                        self.canvas.SetPixel(px, fy, r2, g2, b2)
                    else:
                        self.canvas.SetPixel(px, fy, r, g, b)
                    drawn_pixels.append((px, fy))

        self._last_candle_pixels = drawn_pixels
