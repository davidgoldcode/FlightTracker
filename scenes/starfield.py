import random
import math
from utilities.animator import Animator
from setup import frames


# starfield settings
NUM_STARS = 40
TWINKLE_SPEED = 0.1
SHOOTING_STAR_CHANCE = 0.005  # chance per frame of a shooting star

# star brightness levels (dimmer = further away feeling)
STAR_COLORS = [
    (255, 255, 255),  # bright white
    (200, 200, 220),  # slightly blue
    (180, 180, 180),  # medium
    (120, 120, 140),  # dim
    (80, 80, 100),    # very dim
]


class Star:
    def __init__(self, x, y, brightness_index, phase):
        self.x = x
        self.y = y
        self.brightness_index = brightness_index
        self.phase = phase
        self.twinkle_speed = random.uniform(0.05, 0.15)


class ShootingStar:
    def __init__(self):
        # start from random position on top or right edge
        if random.random() > 0.5:
            self.x = random.randint(20, 63)
            self.y = 0
        else:
            self.x = 63
            self.y = random.randint(0, 15)
        self.speed_x = random.uniform(-2, -1)
        self.speed_y = random.uniform(0.5, 1.5)
        self.trail_length = random.randint(4, 8)
        self.life = 0


class StarfieldScene(object):
    def __init__(self):
        super().__init__()
        self._starfield_stars = []
        self._starfield_shooting_stars = []
        self._starfield_initialized = False
        self._last_star_pixels = []

    def _init_stars(self):
        self._starfield_stars = []
        for _ in range(NUM_STARS):
            x = random.randint(0, 63)
            y = random.randint(0, 31)
            brightness = random.randint(0, len(STAR_COLORS) - 1)
            phase = random.uniform(0, 2 * math.pi)
            self._starfield_stars.append(Star(x, y, brightness, phase))
        self._starfield_initialized = True

    @Animator.KeyFrame.add(frames.PER_SECOND // 10)
    def starfield(self, count):
        # only show when no flights overhead
        if len(self._data):
            # clear stars if flights appear
            if self._last_star_pixels:
                for px, py in self._last_star_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_star_pixels = []
            return

        # initialize stars on first run
        if not self._starfield_initialized:
            self._init_stars()

        drawn_pixels = []

        # clear previous positions
        for px, py in self._last_star_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # update and draw stars
        for star in self._starfield_stars:
            star.phase += star.twinkle_speed
            if star.phase > 2 * math.pi:
                star.phase -= 2 * math.pi

            # twinkle effect: modulate brightness
            twinkle = (math.sin(star.phase) + 1) / 2  # 0 to 1
            base_color = STAR_COLORS[star.brightness_index]
            r = int(base_color[0] * (0.3 + 0.7 * twinkle))
            g = int(base_color[1] * (0.3 + 0.7 * twinkle))
            b = int(base_color[2] * (0.3 + 0.7 * twinkle))

            self.canvas.SetPixel(star.x, star.y, r, g, b)
            drawn_pixels.append((star.x, star.y))

        # maybe spawn shooting star
        if random.random() < SHOOTING_STAR_CHANCE:
            self._starfield_shooting_stars.append(ShootingStar())

        # update shooting stars
        new_shooting_stars = []
        for ss in self._starfield_shooting_stars:
            ss.x += ss.speed_x
            ss.y += ss.speed_y
            ss.life += 1

            # draw trail
            for i in range(ss.trail_length):
                trail_x = int(ss.x - ss.speed_x * i * 0.5)
                trail_y = int(ss.y - ss.speed_y * i * 0.5)
                if 0 <= trail_x < 64 and 0 <= trail_y < 32:
                    # fade trail
                    fade = 1 - (i / ss.trail_length)
                    r = int(255 * fade)
                    g = int(255 * fade)
                    b = int(200 * fade)
                    self.canvas.SetPixel(trail_x, trail_y, r, g, b)
                    drawn_pixels.append((trail_x, trail_y))

            # keep if still on screen
            if 0 <= ss.x < 64 and 0 <= ss.y < 32:
                new_shooting_stars.append(ss)

        self._starfield_shooting_stars = new_shooting_stars
        self._last_star_pixels = drawn_pixels
