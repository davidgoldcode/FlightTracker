import random
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

# load messages from config with graceful fallback
def _load_messages():
    try:
        from config import LOVE_MESSAGES
        # validate: must be a non-empty list of non-empty strings
        if not isinstance(LOVE_MESSAGES, (list, tuple)):
            return DEFAULT_MESSAGES
        valid = [m for m in LOVE_MESSAGES if isinstance(m, str) and m.strip()]
        return valid if valid else DEFAULT_MESSAGES
    except (ImportError, NameError, AttributeError):
        return DEFAULT_MESSAGES

MESSAGES = _load_messages()

# display settings
MESSAGE_Y = 20  # vertical position (centered on 32px display)
SCROLL_SPEED = 1  # pixels per frame
PAUSE_FRAMES = 90  # pause when message is centered (~3 sec at 30fps)
MESSAGE_COLOR = graphics.Color(255, 150, 200)  # soft pink


class LoveMessagesScene(object):
    def __init__(self):
        super().__init__()
        self._message_index = 0
        self._lovemsg_scroll_x = 64  # start off-screen right
        self._pause_counter = 0
        self._current_message = MESSAGES[0]
        self._message_width = 0

    def _get_message_width(self, message):
        # approximate width: 5 pixels per character for 4x6 font
        return len(message) * 5

    @Animator.KeyFrame.add(1)  # run every frame for smooth scrolling
    def love_messages(self, count):
        # only show when no flights overhead
        if len(self._data):
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        # clear previous message area
        for x in range(64):
            for y in range(MESSAGE_Y - 6, MESSAGE_Y + 2):
                if 0 <= y < 32:
                    self.canvas.SetPixel(x, y, 0, 0, 0)

        # calculate message width if not set
        if self._message_width == 0:
            self._message_width = self._get_message_width(self._current_message)

        # calculate center position
        center_x = (64 - self._message_width) // 2

        # check if message is centered (pause)
        if abs(self._lovemsg_scroll_x - center_x) < 2:
            self._pause_counter += 1
            if self._pause_counter < PAUSE_FRAMES:
                # draw message at center during pause
                graphics.DrawText(
                    self.canvas,
                    fonts.extrasmall,
                    center_x,
                    MESSAGE_Y,
                    MESSAGE_COLOR,
                    self._current_message
                )
                return
            # pause done, continue scrolling
        else:
            self._pause_counter = 0

        # scroll left
        self._lovemsg_scroll_x -= SCROLL_SPEED

        # draw message
        graphics.DrawText(
            self.canvas,
            fonts.extrasmall,
            self._lovemsg_scroll_x,
            MESSAGE_Y,
            MESSAGE_COLOR,
            self._current_message
        )

        # check if message scrolled off-screen left
        if self._lovemsg_scroll_x < -self._message_width:
            # next message
            self._message_index = (self._message_index + 1) % len(MESSAGES)
            self._current_message = MESSAGES[self._message_index]
            self._message_width = self._get_message_width(self._current_message)
            self._lovemsg_scroll_x = 64  # reset to right side
            self._pause_counter = 0
