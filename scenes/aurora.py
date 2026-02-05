import math
import random
from utilities.animator import Animator
from setup import frames


# aurora colors: green, blue, purple, cyan
AURORA_COLORS = [
    (0, 255, 100),    # bright green
    (0, 200, 150),    # teal
    (50, 150, 255),   # light blue
    (100, 50, 255),   # purple
    (150, 0, 200),    # magenta
]

# animation settings
NUM_BANDS = 5
WAVE_SPEED = 0.03
VERTICAL_DRIFT_SPEED = 0.02


class AuroraBand:
    def __init__(self, y_base, color_idx):
        self.y_base = y_base
        self.color_idx = color_idx
        self.phase = random.uniform(0, 2 * math.pi)
        self.freq = random.uniform(0.05, 0.12)
        self.amplitude = random.uniform(2, 5)
        self.intensity = random.uniform(0.5, 1.0)
        self.drift_phase = random.uniform(0, 2 * math.pi)


class AuroraScene(object):
    def __init__(self):
        super().__init__()
        self._aurora_bands = []
        self._aurora_initialized = False
        self._last_aurora_pixels = []
        self._aurora_time = 0.0

    def _init_aurora(self):
        self._aurora_bands = []
        for i in range(NUM_BANDS):
            y_base = 5 + i * 5  # spread bands vertically
            color_idx = i % len(AURORA_COLORS)
            self._aurora_bands.append(AuroraBand(y_base, color_idx))
        self._aurora_initialized = True

    @Animator.KeyFrame.add(1)
    def zzz_aurora(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_aurora_pixels:
                for px, py in self._last_aurora_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_aurora_pixels = []
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        if not self._aurora_initialized:
            self._init_aurora()

        drawn_pixels = []
        self._aurora_time += WAVE_SPEED

        # clear previous
        for px, py in self._last_aurora_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # draw each band
        for band in self._aurora_bands:
            band.phase += band.freq
            band.drift_phase += VERTICAL_DRIFT_SPEED

            # vertical drift
            y_offset = math.sin(band.drift_phase) * 2

            for x in range(64):
                # wave motion
                wave = math.sin(x * 0.1 + band.phase + self._aurora_time)
                y = int(band.y_base + wave * band.amplitude + y_offset)

                # intensity variation along the band
                intensity_mod = (math.sin(x * 0.05 + self._aurora_time * 0.5) + 1) / 2
                intensity = band.intensity * (0.3 + 0.7 * intensity_mod)

                # get base color and apply intensity
                base_r, base_g, base_b = AURORA_COLORS[band.color_idx]

                # draw vertical gradient (curtain effect)
                for dy in range(-2, 4):
                    py = y + dy
                    if 0 <= py < 32:
                        # fade based on distance from center
                        fade = 1 - abs(dy) / 4
                        fade = max(0, fade)

                        r = int(base_r * intensity * fade)
                        g = int(base_g * intensity * fade)
                        b = int(base_b * intensity * fade)

                        # blend with existing pixel (for overlapping bands)
                        # simple additive blend, capped at 255
                        r = min(255, r)
                        g = min(255, g)
                        b = min(255, b)

                        if r > 0 or g > 0 or b > 0:
                            self.canvas.SetPixel(x, py, r, g, b)
                            drawn_pixels.append((x, py))

        self._last_aurora_pixels = drawn_pixels
