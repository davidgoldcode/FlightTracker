import random
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

# rain settings
NUM_RAINDROPS = 60
RAIN_SPEED_MIN = 1.5
RAIN_SPEED_MAX = 3.0
RAIN_COLOR = (100, 150, 200)
LIGHTNING_CHANCE = 0.01  # per frame
LIGHTNING_DURATION = 3  # frames


class Raindrop:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, 63)
        self.y = random.uniform(-5, 0)
        self.speed = random.uniform(RAIN_SPEED_MIN, RAIN_SPEED_MAX)
        self.length = random.randint(2, 4)
        self.brightness = random.uniform(0.5, 1.0)


class RainScene(object):
    def __init__(self):
        super().__init__()
        self._raindrops = []
        self._rain_initialized = False
        self._last_rain_pixels = []
        self._lightning_frames = 0
        self._puddles = [0] * 64  # splash effect at bottom

    def _init_rain(self):
        self._raindrops = [Raindrop() for _ in range(NUM_RAINDROPS)]
        # spread initial drops across screen
        for drop in self._raindrops:
            drop.y = random.uniform(0, 31)
        self._rain_initialized = True

    @Animator.KeyFrame.add(1)
    def rain(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_rain_pixels:
                for px, py in self._last_rain_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_rain_pixels = []
            return

        # only show in demo/test mode
        if not DEMO_MODE:
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        if not self._rain_initialized:
            self._init_rain()

        drawn_pixels = []

        # clear previous
        for px, py in self._last_rain_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # check for lightning
        if self._lightning_frames > 0:
            self._lightning_frames -= 1
            # flash the screen
            flash_intensity = int(200 * (self._lightning_frames / LIGHTNING_DURATION))
            for x in range(64):
                for y in range(32):
                    self.canvas.SetPixel(x, y, flash_intensity, flash_intensity, flash_intensity + 50)
                    drawn_pixels.append((x, y))
            self._last_rain_pixels = drawn_pixels
            return

        # maybe trigger lightning
        if random.random() < LIGHTNING_CHANCE:
            self._lightning_frames = LIGHTNING_DURATION

        # dark stormy background (subtle)
        for x in range(64):
            for y in range(10):
                # dark clouds at top
                cloud_intensity = int(15 * (1 - y / 10))
                if random.random() < 0.3:  # sparse clouds
                    self.canvas.SetPixel(x, y, cloud_intensity, cloud_intensity, cloud_intensity + 5)
                    drawn_pixels.append((x, y))

        # update and draw raindrops
        for drop in self._raindrops:
            drop.y += drop.speed

            # splash at bottom
            if drop.y >= 30:
                self._puddles[drop.x] = min(3, self._puddles[drop.x] + 1)
                drop.reset()
                continue

            # draw raindrop (vertical line)
            px = int(drop.x)
            for i in range(drop.length):
                py = int(drop.y) - i
                if 0 <= py < 32:
                    # fade toward tail
                    fade = 1 - (i / drop.length) * 0.5
                    r = int(RAIN_COLOR[0] * drop.brightness * fade)
                    g = int(RAIN_COLOR[1] * drop.brightness * fade)
                    b = int(RAIN_COLOR[2] * drop.brightness * fade)
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        # draw and decay puddles/splashes at bottom
        for x in range(64):
            if self._puddles[x] > 0:
                # splash ripple
                for dx in range(-self._puddles[x], self._puddles[x] + 1):
                    px = x + dx
                    if 0 <= px < 64:
                        intensity = int(80 * (1 - abs(dx) / (self._puddles[x] + 1)))
                        self.canvas.SetPixel(px, 31, intensity, intensity, intensity + 30)
                        drawn_pixels.append((px, 31))
                # decay puddle
                if random.random() < 0.2:
                    self._puddles[x] -= 1

        self._last_rain_pixels = drawn_pixels
