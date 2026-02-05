import math
import random
import time

from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


# default messages (used if config is missing or invalid)
DEFAULT_MESSAGES = [
    "I love you",
    "You're amazing",
    "Thinking of you",
    "Miss you",
    "You make me happy",
    "XOXO",
    "Forever yours",
    "My favorite person",
]

DEFAULT_QUOTES = [
    "Be the change",
    "Stay curious",
    "One day at a time",
    "Do what you love",
]


# load lists from config with graceful fallback
def _load_messages():
    try:
        from config import LOVE_MESSAGES
        if not isinstance(LOVE_MESSAGES, (list, tuple)):
            return DEFAULT_MESSAGES
        valid = [m for m in LOVE_MESSAGES if isinstance(m, str) and m.strip()]
        return valid if valid else DEFAULT_MESSAGES
    except (ImportError, NameError, AttributeError):
        return DEFAULT_MESSAGES


def _load_quotes():
    try:
        from config import QUOTES
        if not isinstance(QUOTES, (list, tuple)):
            return DEFAULT_QUOTES
        valid = [q for q in QUOTES if isinstance(q, str) and q.strip()]
        return valid if valid else DEFAULT_QUOTES
    except (ImportError, NameError, AttributeError):
        return DEFAULT_QUOTES


def _is_demo_mode():
    try:
        from config import ZONE_HOME
        return False
    except (ImportError, NameError, AttributeError):
        return True


MESSAGES = _load_messages()
QUOTES = _load_quotes()
ALL_MESSAGES = MESSAGES + QUOTES
if not ALL_MESSAGES:
    ALL_MESSAGES = DEFAULT_MESSAGES + DEFAULT_QUOTES
DEMO_MODE = _is_demo_mode()

# timing
MIN_INTERVAL = 3600     # 60 minutes between appearances
MAX_INTERVAL = 5400     # 90 minutes between appearances
DISPLAY_DURATION = 180  # 3 minutes max on screen
DEMO_INITIAL_DELAY = 2  # seconds before first message in demo mode

# display settings
MESSAGE_Y = 22
SCROLL_SPEED = 1
PAUSE_FRAMES = 80  # ~8 seconds at 10fps
MESSAGE_COLOR = graphics.Color(255, 150, 200)

# heart shape (8x6 pixels, same as heartbeat scene)
HEART_PIXELS = [
    (1, 0), (2, 0), (5, 0), (6, 0),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
    (2, 4), (3, 4), (4, 4), (5, 4),
    (3, 5), (4, 5),
]
HEART_X = 28  # centered on 64px display
HEART_Y = 10

# pulse settings
PULSE_SPEED = 0.15
PULSE_MIN = 0.3
PULSE_MAX = 1.0


class LoveMessagesScene(object):
    def __init__(self):
        super().__init__()
        self._msg_active = False
        initial_delay = DEMO_INITIAL_DELAY if DEMO_MODE else random.randint(MIN_INTERVAL, MAX_INTERVAL)
        self._msg_next_time = time.time() + initial_delay
        self._msg_start_time = 0
        self._msg_scroll_x = 64
        self._msg_pause_counter = 0
        self._msg_current = ""
        self._msg_width = 0
        self._msg_heart_phase = 0.0
        self._msg_last_heart_pixels = []

    def _get_message_width(self, message):
        # ~5 pixels per character for extrasmall font (4x6 with spacing)
        return len(message) * 5

    def _draw_heart(self, brightness):
        base_r, base_g, base_b = 255, 20, 60
        r = int(base_r * brightness)
        g = int(base_g * brightness)
        b = int(base_b * brightness)

        pixels = []
        for hx, hy in HEART_PIXELS:
            px = HEART_X + hx
            py = HEART_Y + hy
            self.canvas.SetPixel(px, py, r, g, b)
            pixels.append((px, py))
        return pixels

    def _clear_areas(self):
        # clear heart
        for px, py in self._msg_last_heart_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)
        self._msg_last_heart_pixels = []
        for hx, hy in HEART_PIXELS:
            self.canvas.SetPixel(HEART_X + hx, HEART_Y + hy, 0, 0, 0)

        # clear text area
        for x in range(64):
            for y in range(MESSAGE_Y - 6, MESSAGE_Y + 2):
                if 0 <= y < 32:
                    self.canvas.SetPixel(x, y, 0, 0, 0)

    def _activate(self):
        self._msg_active = True
        self._msg_start_time = time.time()
        self._msg_heart_phase = 0.0
        self._pick_message()

    def _pick_message(self):
        self._msg_current = random.choice(ALL_MESSAGES)
        self._msg_width = self._get_message_width(self._msg_current)
        self._msg_scroll_x = 64
        self._msg_pause_counter = 0

    def _deactivate(self):
        self._msg_active = False
        self._msg_next_time = time.time() + random.randint(MIN_INTERVAL, MAX_INTERVAL)
        self._clear_areas()

    # named heart_and_message so it sorts before heartbeat alphabetically
    # (keyframes execute in dir() order). when active, this claims the
    # frame and heartbeat skips. when inactive, heartbeat draws normally.
    @Animator.KeyFrame.add(1)
    def heart_and_message(self, count):
        # flights take priority
        if len(self._data):
            if self._msg_active:
                self._deactivate()
            return

        now = time.time()

        # check if it's time to activate
        if not self._msg_active:
            if now >= self._msg_next_time:
                self._activate()
            else:
                return

        # check 3-minute timeout
        if now - self._msg_start_time >= DISPLAY_DURATION:
            self._deactivate()
            return

        # claim the frame (prevents heartbeat from drawing)
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        # clear text area for redraw
        for x in range(64):
            for y in range(MESSAGE_Y - 6, MESSAGE_Y + 2):
                if 0 <= y < 32:
                    self.canvas.SetPixel(x, y, 0, 0, 0)

        # pulse heart
        self._msg_heart_phase += PULSE_SPEED
        if self._msg_heart_phase > 2 * math.pi:
            self._msg_heart_phase -= 2 * math.pi
        pulse = (math.sin(self._msg_heart_phase) + 1) / 2
        brightness = PULSE_MIN + (PULSE_MAX - PULSE_MIN) * pulse
        self._msg_last_heart_pixels = self._draw_heart(brightness)

        # short messages pause centered, long ones scroll through
        if self._msg_width <= 64:
            center_x = (64 - self._msg_width) // 2
            if abs(self._msg_scroll_x - center_x) < 2:
                self._msg_pause_counter += 1
                if self._msg_pause_counter < PAUSE_FRAMES:
                    graphics.DrawText(
                        self.canvas, fonts.extrasmall,
                        center_x, MESSAGE_Y,
                        MESSAGE_COLOR, self._msg_current
                    )
                    return
            else:
                self._msg_pause_counter = 0

        # scroll left
        self._msg_scroll_x -= SCROLL_SPEED

        # draw message
        graphics.DrawText(
            self.canvas, fonts.extrasmall,
            self._msg_scroll_x, MESSAGE_Y,
            MESSAGE_COLOR, self._msg_current
        )

        # scrolled off screen - pick next message
        if self._msg_scroll_x < -self._msg_width:
            self._pick_message()
