import random
import math
from utilities.animator import Animator
from setup import frames


# fire colors from hottest to coolest
FIRE_COLORS = [
    (255, 255, 200),  # white/yellow (hottest)
    (255, 200, 50),   # bright yellow
    (255, 150, 0),    # orange
    (255, 80, 0),     # red-orange
    (200, 30, 0),     # red
    (100, 10, 0),     # dark red
    (50, 5, 0),       # embers
]

# fireplace dimensions
FIRE_WIDTH = 40
FIRE_HEIGHT = 20
FIRE_X_OFFSET = 12  # center on 64px display
FIRE_Y_OFFSET = 12  # bottom portion of display


class FireplaceScene(object):
    def __init__(self):
        super().__init__()
        self._fire_grid = []
        self._fire_initialized = False
        self._last_fire_pixels = []

    def _init_fire(self):
        # create cooling map
        self._fire_grid = [[0] * FIRE_WIDTH for _ in range(FIRE_HEIGHT)]
        self._fire_initialized = True

    def _get_fire_color(self, intensity):
        # map intensity (0-255) to color
        if intensity <= 0:
            return (0, 0, 0)

        # normalize to color index
        idx = int((1 - intensity / 255) * (len(FIRE_COLORS) - 1))
        idx = max(0, min(len(FIRE_COLORS) - 1, idx))

        r, g, b = FIRE_COLORS[idx]
        # apply intensity
        factor = intensity / 255
        return (int(r * factor), int(g * factor), int(b * factor))

    @Animator.KeyFrame.add(1)
    def fireplace(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_fire_pixels:
                for px, py in self._last_fire_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_fire_pixels = []
            return

        if not self._fire_initialized:
            self._init_fire()

        drawn_pixels = []

        # clear previous
        for px, py in self._last_fire_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # generate heat at bottom
        for x in range(FIRE_WIDTH):
            # random heat at base with some variation
            heat = random.randint(180, 255)
            # create gaps for flickering effect
            if random.random() < 0.3:
                heat = random.randint(100, 180)
            self._fire_grid[FIRE_HEIGHT - 1][x] = heat

        # propagate fire upward with cooling
        for y in range(FIRE_HEIGHT - 2, -1, -1):
            for x in range(FIRE_WIDTH):
                # sample from below with slight randomness
                below_left = self._fire_grid[y + 1][max(0, x - 1)]
                below = self._fire_grid[y + 1][x]
                below_right = self._fire_grid[y + 1][min(FIRE_WIDTH - 1, x + 1)]

                # average with wind drift
                avg = (below_left + below + below + below_right) // 4

                # cooling factor (more cooling higher up)
                cooling = random.randint(10, 30) + y
                self._fire_grid[y][x] = max(0, avg - cooling)

        # draw fire
        for y in range(FIRE_HEIGHT):
            for x in range(FIRE_WIDTH):
                intensity = self._fire_grid[y][x]
                if intensity > 10:  # skip very dark pixels
                    px = FIRE_X_OFFSET + x
                    py = FIRE_Y_OFFSET + y
                    if 0 <= px < 64 and 0 <= py < 32:
                        r, g, b = self._get_fire_color(intensity)
                        self.canvas.SetPixel(px, py, r, g, b)
                        drawn_pixels.append((px, py))

        # draw log/base
        for x in range(FIRE_WIDTH - 4):
            px = FIRE_X_OFFSET + x + 2
            py = 31
            self.canvas.SetPixel(px, py, 60, 30, 10)
            drawn_pixels.append((px, py))

        self._last_fire_pixels = drawn_pixels
