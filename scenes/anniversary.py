import math
import random
from datetime import datetime, timedelta
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


# try to load anniversary config
def _load_anniversary():
    try:
        from config import ANNIVERSARY
        return ANNIVERSARY
    except (ImportError, NameError):
        return None

def _is_demo_mode():
    """Check if running in test/demo mode (no config or testing)."""
    try:
        from config import ANNIVERSARY
        return False  # config exists, use real logic
    except (ImportError, NameError):
        return True  # no config, demo mode

ANNIVERSARY_DATE = _load_anniversary()
DEMO_MODE = _is_demo_mode()

# confetti colors
CONFETTI_COLORS = [
    (255, 100, 150),  # pink
    (255, 50, 100),   # red
    (255, 200, 100),  # gold
    (255, 255, 200),  # cream
]


class Confetti:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)
        self.speed = random.uniform(0.2, 0.6)
        self.drift = random.uniform(-0.2, 0.2)
        self.color = random.choice(CONFETTI_COLORS)


class AnniversaryScene(object):
    def __init__(self):
        super().__init__()
        self._anniversary_confetti = [Confetti() for _ in range(25)]
        self._last_anniversary_pixels = []
        self._heart_phase = 0
        self._anniversary_scroll_x = 64  # for scrolling text
        # for testing scenarios
        self._scenario_days = None  # None = use real date, number = simulate X days until

    def _anniversary_get_days_until(self):
        if not ANNIVERSARY_DATE:
            return None

        today = datetime.now()
        try:
            month, day = map(int, ANNIVERSARY_DATE.split("-"))
            year = today.year

            # handle Feb 29 on non-leap years (use Feb 28)
            import calendar
            if month == 2 and day == 29 and not calendar.isleap(year):
                day = 28

            anniversary_this_year = datetime(year, month, day)
            if anniversary_this_year < today:
                year += 1
                # check leap year again for next year
                if month == 2 and day == 29 and not calendar.isleap(year):
                    day = 28
                anniversary_this_year = datetime(year, month, day)

            delta = anniversary_this_year - today
            return delta.days
        except (ValueError, AttributeError):
            return None

    def _is_anniversary_today(self):
        if not ANNIVERSARY_DATE:
            return False
        today = datetime.now().strftime("%m-%d")
        return today == ANNIVERSARY_DATE

    @Animator.KeyFrame.add(1)
    def anniversary(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_anniversary_pixels:
                for px, py in self._last_anniversary_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_anniversary_pixels = []
            return

        # in demo mode, simulate scenario or default countdown
        if DEMO_MODE:
            if self._scenario_days is not None:
                days = self._scenario_days
            else:
                days = 5  # default demo: 5 days until anniversary
        else:
            if not ANNIVERSARY_DATE:
                return

            days = self._anniversary_get_days_until()
            if days is None:
                return

            # only show when within 7 days or on the day
            if days > 7 and not self._is_anniversary_today():
                return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_anniversary_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._heart_phase += 0.1

        # check if it's the anniversary day (real check or scenario)
        is_today = self._is_anniversary_today() or (DEMO_MODE and days == 0)
        if is_today:
            # celebration mode - full confetti and scrolling message
            message = "Happy Anniversary!"

            # pulsing text
            pulse = 0.7 + 0.3 * math.sin(self._heart_phase)
            text_color = graphics.Color(
                int(255 * pulse),
                int(150 * pulse),
                int(200 * pulse)
            )

            # scrolling text (too long to fit on 64px display)
            graphics.DrawText(
                self.canvas,
                fonts.extrasmall,
                int(self._anniversary_scroll_x),
                16,
                text_color,
                message
            )
            # mark text area as drawn
            for tx in range(int(self._anniversary_scroll_x), min(64, int(self._anniversary_scroll_x) + len(message) * 5)):
                if 0 <= tx < 64:
                    for ty in range(10, 18):
                        drawn_pixels.append((tx, ty))

            # scroll the text
            self._anniversary_scroll_x -= 0.5
            if self._anniversary_scroll_x < -len(message) * 5:
                self._anniversary_scroll_x = 64

            # lots of confetti
            for conf in self._anniversary_confetti:
                conf.y += conf.speed
                conf.x += conf.drift

                if conf.y > 32:
                    conf.reset()
                    continue

                px = int(conf.x) % 64
                py = int(conf.y)
                if 0 <= py < 32:
                    r, g, b = conf.color
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        else:
            # countdown mode
            day_word = "day" if days == 1 else "days"
            message = f"{days} {day_word}"
            text_color = graphics.Color(255, 150, 200)

            # draw countdown
            x = (64 - len(message) * 4) // 2
            graphics.DrawText(self.canvas, fonts.extrasmall, x, 20, text_color, message)
            for tx in range(x, min(64, x + len(message) * 4)):
                for ty in range(14, 22):
                    drawn_pixels.append((tx, ty))

            # draw small heart above
            heart_x = 28
            heart_y = 8
            pulse = 0.8 + 0.2 * math.sin(self._heart_phase)
            r = int(255 * pulse)
            g = int(50 * pulse)
            b = int(80 * pulse)

            # small 5x4 heart
            heart = [
                (1, 0), (2, 0), (4, 0), (5, 0),
                (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
                (2, 3), (3, 3), (4, 3),
                (3, 4),
            ]
            for hx, hy in heart:
                px = heart_x + hx
                py = heart_y + hy
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, r, g, b)
                    drawn_pixels.append((px, py))

        self._last_anniversary_pixels = drawn_pixels
