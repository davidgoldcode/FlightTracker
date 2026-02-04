import math
import random
from datetime import datetime
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


# default countdown days (can be overridden per person)
DEFAULT_COUNTDOWN_DAYS = 3

# try to load birthday config
def _load_birthday_config():
    try:
        from config import MY_BIRTHDAY, PARTNER_BIRTHDAY
        birthdays = {"Me": MY_BIRTHDAY, "Partner": PARTNER_BIRTHDAY}
    except (ImportError, NameError):
        birthdays = {}

    try:
        from config import OTHER_BIRTHDAYS
        if isinstance(OTHER_BIRTHDAYS, dict):
            birthdays.update(OTHER_BIRTHDAYS)
    except (ImportError, NameError):
        pass

    return birthdays


def _load_countdown_days():
    try:
        from config import BIRTHDAY_COUNTDOWN_DAYS
        return BIRTHDAY_COUNTDOWN_DAYS
    except (ImportError, NameError):
        return DEFAULT_COUNTDOWN_DAYS


def _is_demo_mode():
    """Check if running in test/demo mode (no config or testing)."""
    try:
        from config import MY_BIRTHDAY
        return False  # config exists, use real logic
    except (ImportError, NameError):
        return True  # no config, demo mode


BIRTHDAYS = _load_birthday_config()
COUNTDOWN_DAYS = _load_countdown_days()
DEMO_MODE = _is_demo_mode()

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
        self._birthday_confetti = [Confetti() for _ in range(30)]
        self._birthday_scroll_x = 64
        self._last_birthday_pixels = []
        self._flame_phase = 0
        # for testing scenarios
        self._scenario_days = None  # None = use real date, number = simulate X days until

    def _get_birthday_info(self, name, date_val):
        """Get birthday date and countdown days for a person.

        date_val can be:
        - a string like "03-15" (uses global countdown days)
        - a dict like {"date": "03-15", "countdown": 5} (custom countdown)
        """
        if isinstance(date_val, dict):
            date = date_val.get("date", "")
            countdown = date_val.get("countdown", COUNTDOWN_DAYS)
        else:
            date = date_val
            countdown = COUNTDOWN_DAYS
        return date, countdown

    def _get_days_until(self, date_str):
        """Calculate days until a birthday."""
        today = datetime.now()
        try:
            month, day = map(int, date_str.split("-"))
            year = today.year

            # handle Feb 29 on non-leap years (use Feb 28)
            if month == 2 and day == 29:
                import calendar
                if not calendar.isleap(year):
                    day = 28

            birthday_this_year = datetime(year, month, day)
            if birthday_this_year.date() < today.date():
                year += 1
                # check leap year again for next year
                if month == 2 and day == 29 and not calendar.isleap(year):
                    day = 28
                birthday_this_year = datetime(year, month, day)

            delta = birthday_this_year.date() - today.date()
            return delta.days
        except (ValueError, AttributeError):
            return None

    def _check_birthday_or_countdown(self):
        """Check if today is someone's birthday OR within countdown range.

        Returns: (name, days_until, is_today) or (None, None, False)
        """
        today = datetime.now().strftime("%m-%d")

        for name, date_val in BIRTHDAYS.items():
            date, countdown_days = self._get_birthday_info(name, date_val)

            if not date:
                continue

            # check if today is the birthday
            if date == today:
                return (name, 0, True)

            # check countdown (only for OTHER_BIRTHDAYS, not Me/Partner)
            if name not in ("Me", "Partner") and countdown_days > 0:
                days = self._get_days_until(date)
                if days is not None and 0 < days <= countdown_days:
                    return (name, days, False)

        return (None, None, False)

    @Animator.KeyFrame.add(1)
    def birthday(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_birthday_pixels:
                for px, py in self._last_birthday_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_birthday_pixels = []
            return

        # check for birthday or countdown
        if DEMO_MODE:
            # demo mode: simulate scenario
            if self._scenario_days is not None:
                if self._scenario_days == 0:
                    name, days, is_today = "Mom", 0, True
                else:
                    name, days, is_today = "Mom", self._scenario_days, False
            else:
                # default demo: show countdown
                name, days, is_today = "Demo", 3, False
        else:
            name, days, is_today = self._check_birthday_or_countdown()
            if name is None:
                return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_birthday_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._flame_phase += 0.3

        if is_today:
            # celebration mode - full animation
            self._draw_celebration(drawn_pixels, name)
        else:
            # countdown mode
            self._draw_countdown(drawn_pixels, name, days)

        self._last_birthday_pixels = drawn_pixels

    def _draw_celebration(self, drawn_pixels, name):
        """Draw full birthday celebration with cake and confetti."""
        # draw cake (bottom left)
        cake_x = 4
        cake_y = 24
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
            int(self._birthday_scroll_x),
            10,
            text_color,
            message
        )
        # mark text area as drawn
        for x in range(int(self._birthday_scroll_x), min(64, int(self._birthday_scroll_x) + len(message) * 5)):
            if 0 <= x < 64:
                for y in range(4, 12):
                    drawn_pixels.append((x, y))

        self._birthday_scroll_x -= 0.5
        if self._birthday_scroll_x < -len(message) * 5:
            self._birthday_scroll_x = 64

        # draw confetti
        for conf in self._birthday_confetti:
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

    def _draw_countdown(self, drawn_pixels, name, days):
        """Draw birthday countdown display."""
        # draw small cake icon (top right corner)
        cake_x = 52
        cake_y = 2
        for (cx, cy), (r, g, b) in CAKE_PIXELS:
            px = cake_x + cx
            py = cake_y + cy
            if 0 <= px < 64 and 0 <= py < 32:
                # flicker the flame
                if cy == 0:
                    flicker = 0.7 + 0.3 * math.sin(self._flame_phase)
                    r = int(r * flicker)
                    g = int(g * flicker)
                # draw smaller/dimmer
                self.canvas.SetPixel(px, py, r // 2, g // 2, b // 2)
                drawn_pixels.append((px, py))

        # line 1: "X days until"
        day_word = "day" if days == 1 else "days"
        line1 = f"{days} {day_word} until"
        line1_color = graphics.Color(255, 150, 200)
        graphics.DrawText(self.canvas, fonts.extrasmall, 2, 12, line1_color, line1)
        for x in range(2, min(64, 2 + len(line1) * 5)):
            for y in range(6, 14):
                drawn_pixels.append((x, y))

        # line 2: "Name's bday"
        line2 = f"{name}'s bday"
        line2_color = graphics.Color(255, 200, 100)
        graphics.DrawText(self.canvas, fonts.extrasmall, 2, 24, line2_color, line2)
        for x in range(2, min(64, 2 + len(line2) * 5)):
            for y in range(18, 26):
                drawn_pixels.append((x, y))
