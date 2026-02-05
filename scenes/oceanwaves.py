import math
from utilities.animator import Animator
from setup import frames


def _is_demo_mode():
    try:
        from config import ZONE_HOME
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()

# wave settings
WAVE_SPEED = 0.08
WAVE_HEIGHT = 4
NUM_WAVE_LAYERS = 3

# ocean colors (from deep to surface)
OCEAN_COLORS = [
    (0, 20, 60),     # deep blue
    (0, 40, 100),    # mid blue
    (0, 80, 140),    # surface blue
    (100, 180, 220), # foam/light
]


class OceanWavesScene(object):
    def __init__(self):
        super().__init__()
        self._wave_phase = 0.0
        self._last_wave_pixels = []

    @Animator.KeyFrame.add(1)  # run every frame for smooth waves
    def ocean_waves(self, count):
        # only show when no flights overhead
        if len(self._data):
            # clear waves if flights appear
            if self._last_wave_pixels:
                for px, py in self._last_wave_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_wave_pixels = []
            return

        # only show in demo/test mode
        if not DEMO_MODE:
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        # clear previous positions
        for px, py in self._last_wave_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._wave_phase += WAVE_SPEED

        # draw multiple wave layers from bottom to top
        for layer in range(NUM_WAVE_LAYERS):
            # each layer has different frequency and phase offset
            freq = 0.1 + layer * 0.03
            amplitude = WAVE_HEIGHT - layer
            base_y = 28 - layer * 6  # stack layers from bottom
            phase_offset = layer * 0.5

            for x in range(64):
                # calculate wave height at this x position
                wave_y = math.sin(x * freq + self._wave_phase + phase_offset)
                y = int(base_y + wave_y * amplitude)

                # draw vertical gradient from wave surface down
                for dy in range(8):
                    py = y + dy
                    if 0 <= py < 32:
                        # gradient from surface to deep
                        color_idx = min(dy // 2, len(OCEAN_COLORS) - 1)
                        r, g, b = OCEAN_COLORS[color_idx]

                        # add subtle variation
                        variation = math.sin(x * 0.2 + self._wave_phase * 0.5) * 10
                        r = max(0, min(255, r + int(variation)))
                        g = max(0, min(255, g + int(variation)))

                        self.canvas.SetPixel(x, py, r, g, b)
                        drawn_pixels.append((x, py))

                # foam on wave crests
                if wave_y > 0.7:
                    foam_y = y - 1
                    if 0 <= foam_y < 32:
                        # white foam with slight variation
                        foam_brightness = int(200 + 55 * wave_y)
                        self.canvas.SetPixel(x, foam_y, foam_brightness, foam_brightness, foam_brightness)
                        drawn_pixels.append((x, foam_y))

        self._last_wave_pixels = drawn_pixels
