import math
from utilities.animator import Animator
from setup import colours, frames
from rgbmatrix import graphics


# heart shape (8x6 pixels)
# centered at position for visibility alongside clock/weather
HEART_PIXELS = [
    # row 0: top bumps
    (1, 0), (2, 0), (5, 0), (6, 0),
    # row 1
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
    # row 2
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
    # row 3
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
    # row 4
    (2, 4), (3, 4), (4, 4), (5, 4),
    # row 5: bottom point (two pixels for symmetry)
    (3, 5), (4, 5),
]

# position on display (bottom right area, above weather graph area)
HEART_OFFSET_X = 28
HEART_OFFSET_Y = 12

# animation settings
PULSE_SPEED = 0.15  # radians per frame
PULSE_MIN = 0.3     # minimum brightness multiplier
PULSE_MAX = 1.0     # maximum brightness multiplier


class HeartbeatScene(object):
    def __init__(self):
        super().__init__()
        self._heart_phase = 0.0
        self._last_heart_pixels = []

    @Animator.KeyFrame.add(frames.PER_SECOND // 10)
    def zz_heartbeat(self, count):
        # only show when no flights overhead
        if len(self._data):
            # clear heart if flights appear
            if self._last_heart_pixels:
                for px, py in self._last_heart_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_heart_pixels = []
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        # calculate pulse brightness using sine wave
        self._heart_phase += PULSE_SPEED
        if self._heart_phase > 2 * math.pi:
            self._heart_phase -= 2 * math.pi

        # sine wave oscillates -1 to 1, map to PULSE_MIN to PULSE_MAX
        pulse = (math.sin(self._heart_phase) + 1) / 2  # 0 to 1
        brightness = PULSE_MIN + (PULSE_MAX - PULSE_MIN) * pulse

        # base color: warm red/pink
        base_r = 255
        base_g = 20
        base_b = 60

        # apply brightness
        r = int(base_r * brightness)
        g = int(base_g * brightness)
        b = int(base_b * brightness)

        # draw heart
        drawn_pixels = []
        for hx, hy in HEART_PIXELS:
            px = HEART_OFFSET_X + hx
            py = HEART_OFFSET_Y + hy
            self.canvas.SetPixel(px, py, r, g, b)
            drawn_pixels.append((px, py))

        self._last_heart_pixels = drawn_pixels
