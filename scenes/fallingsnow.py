import random
from utilities.animator import Animator
from setup import frames


# snow settings
NUM_SNOWFLAKES = 50
WIND_DRIFT = 0.3  # horizontal drift


class Snowflake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)  # start above screen
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.choice([1, 1, 1, 2])  # mostly small
        self.brightness = random.randint(180, 255)
        self.drift = random.uniform(-WIND_DRIFT, WIND_DRIFT)


class FallingSnowScene(object):
    def __init__(self):
        super().__init__()
        self._fallingsnow_flakes = []
        self._snow_initialized = False
        self._last_snow_pixels = []
        self._snow_accumulation = [0] * 64  # snow buildup at bottom

    def _init_snow(self):
        self._fallingsnow_flakes = [Snowflake() for _ in range(NUM_SNOWFLAKES)]
        # spread initial snowflakes across screen
        for i, flake in enumerate(self._fallingsnow_flakes):
            flake.y = random.uniform(0, 31)
        self._snow_initialized = True

    @Animator.KeyFrame.add(1)  # run every frame for smooth falling
    def falling_snow(self, count):
        # only show when no flights overhead
        if len(self._data):
            # clear snow if flights appear
            if self._last_snow_pixels:
                for px, py in self._last_snow_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_snow_pixels = []
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        # initialize on first run
        if not self._snow_initialized:
            self._init_snow()

        drawn_pixels = []

        # clear previous positions
        for px, py in self._last_snow_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # update and draw snowflakes
        for flake in self._fallingsnow_flakes:
            # update position
            flake.y += flake.speed
            flake.x += flake.drift + random.uniform(-0.1, 0.1)  # slight random wobble

            # wrap horizontally
            if flake.x < 0:
                flake.x = 63
            elif flake.x > 63:
                flake.x = 0

            # check if landed
            floor_y = 31 - self._snow_accumulation[int(flake.x)]
            if flake.y >= floor_y:
                # accumulate snow (slowly)
                if random.random() < 0.02 and self._snow_accumulation[int(flake.x)] < 5:
                    self._snow_accumulation[int(flake.x)] += 1
                flake.reset()
                continue

            # draw snowflake
            px = int(flake.x)
            py = int(flake.y)
            if 0 <= px < 64 and 0 <= py < 32:
                b = flake.brightness
                self.canvas.SetPixel(px, py, b, b, b)
                drawn_pixels.append((px, py))

                # larger snowflakes
                if flake.size == 2:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < 64 and 0 <= ny < 32:
                            dim = b // 2
                            self.canvas.SetPixel(nx, ny, dim, dim, dim)
                            drawn_pixels.append((nx, ny))

        # draw accumulated snow at bottom
        for x in range(64):
            height = self._snow_accumulation[x]
            for dy in range(height):
                y = 31 - dy
                # slight color variation for texture
                b = 200 + random.randint(-20, 20)
                self.canvas.SetPixel(x, y, b, b, b)
                drawn_pixels.append((x, y))

        # slowly melt accumulated snow
        if random.random() < 0.01:
            x = random.randint(0, 63)
            if self._snow_accumulation[x] > 0:
                self._snow_accumulation[x] -= 1

        self._last_snow_pixels = drawn_pixels
