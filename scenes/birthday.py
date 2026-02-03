import math
import random
from datetime import datetime
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


# try to load birthday config
def _load_birthday_config():
    try:
        from config import MY_BIRTHDAY, PARTNER_BIRTHDAY, OTHER_BIRTHDAYS
        birthdays = {"Me": MY_BIRTHDAY, "Partner": PARTNER_BIRTHDAY}
        if isinstance(OTHER_BIRTHDAYS, dict):
            birthdays.update(OTHER_BIRTHDAYS)
        return birthdays
    except (ImportError, NameError):
        return {}

BIRTHDAYS = _load_birthday_config()

# cake pixels (simple 8x7 cake with candle)
CAKE_PIXELS = [
    # candle flame (yellow)
    ((4, 0), (255, 200, 50)),
    # candle (white)
    ((4, 1), (255, 255, 255)),
    ((4, 2), (255, 255, 255)),
    # frosting top (pink)
    ((1, 3), (255, 150, 200)), ((2, 3), (255, 150, 200)), ((3, 3), (255, 150, 200)),
    ((4, 3), (255, 150, 200)), ((5, 3), (255, 150, 200)), ((6, 3), (255, 150, 200)),
    ((7, 3), (255, 150, 200)),
    # cake body (brown)
    ((0, 4), (180, 100, 50)), ((1, 4), (180, 100, 50)), ((2, 4), (180, 100, 50)),
    ((3, 4), (180, 100, 50)), ((4, 4), (180, 100, 50)), ((5, 4), (180, 100, 50)),
    ((6, 4), (180, 100, 50)), ((7, 4), (180, 100, 50)), ((8, 4), (180, 100, 50)),
    ((0, 5), (180, 100, 50)), ((1, 5), (180, 100, 50)), ((2, 5), (180, 100, 50)),
    ((3, 5), (180, 100, 50)), ((4, 5), (180, 100, 50)), ((5, 5), (180, 100, 50)),
    ((6, 5), (180, 100, 50)), ((7, 5), (180, 100, 50)), ((8, 5), (180, 100, 50)),
    ((0, 6), (180, 100, 50)), ((1, 6), (180, 100, 50)), ((2, 6), (180, 100, 50)),
    ((3, 6), (180, 100, 50)), ((4, 6), (180, 100, 50)), ((5, 6), (180, 100, 50)),
    ((6, 6), (180, 100, 50)), ((7, 6), (180, 100, 50)), ((8, 6), (180, 100, 50)),
]

# confetti colors
CONFETTI_COLORS = [
    (255, 100, 100),  # red
    (100, 255, 100),  # green
    (100, 100, 255),  # blue
    (255, 255, 100),  # yellow
    (255, 100, 255),  # magenta
    (100, 255, 255),  # cyan
]


class Confetti:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)
        self.speed = random.uniform(0.3, 0.8)
        self.drift = random.uniform(-0.3, 0.3)
        self.color = random.choice(CONFETTI_COLORS)
        self.spin = random.uniform(0, 2 * math.pi)
        self.spin_speed = random.uniform(0.1, 0.3)


class BirthdayScene(object):
    def __init__(self):
        super().__init__()
        self._birthday_name = None
        self._confetti = [Confetti() for _ in range(30)]
        self._scroll_x = 64
        self._last_birthday_pixels = []
        self._flame_phase = 0

    def _check_birthday(self):
        today = datetime.now().strftime("%m-%d")
        for name, date in BIRTHDAYS.items():
            if date == today:
                return name
        return None

    @Animator.KeyFrame.add(1)
    def birthday(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_birthday_pixels:
                for px, py in self._last_birthday_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_birthday_pixels = []
            return

        # check if today is someone's birthday
        name = self._check_birthday()
        if not name:
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_birthday_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        # draw cake (bottom left)
        cake_x = 4
        cake_y = 24
        self._flame_phase += 0.3
        for (cx, cy), (r, g, b) in CAKE_PIXELS:
            px = cake_x + cx
            py = cake_y + cy
            if 0 <= px < 64 and 0 <= py < 32:
                # flicker the flame
                if cy == 0:  # flame
                    flicker = 0.7 + 0.3 * math.sin(self._flame_phase)
                    r = int(r * flicker)
                    g = int(g * flicker)
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))

        # draw "Happy Birthday [Name]!" scrolling text
        message = f"Happy Birthday {name}!"
        text_color = graphics.Color(255, 220, 100)
        graphics.DrawText(
            self.canvas,
            fonts.extrasmall,
            int(self._scroll_x),
            10,
            text_color,
            message
        )
        # mark text area as drawn
        for x in range(int(self._scroll_x), min(64, int(self._scroll_x) + len(message) * 5)):
            if 0 <= x < 64:
                for y in range(4, 12):
                    drawn_pixels.append((x, y))

        self._scroll_x -= 0.5
        if self._scroll_x < -len(message) * 5:
            self._scroll_x = 64

        # draw confetti
        for conf in self._confetti:
            conf.y += conf.speed
            conf.x += conf.drift
            conf.spin += conf.spin_speed

            if conf.y > 32:
                conf.reset()
                continue

            px = int(conf.x) % 64
            py = int(conf.y)
            if 0 <= py < 32:
                r, g, b = conf.color
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))

        self._last_birthday_pixels = drawn_pixels
