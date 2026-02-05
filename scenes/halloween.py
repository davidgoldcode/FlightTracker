import math
import random
from datetime import datetime
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


def _is_demo_mode():
    """Check if running in test/demo mode."""
    try:
        from config import HOLIDAYS
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()

# pumpkin sprite (7x6)
PUMPKIN_PIXELS = [
    # stem (green)
    ((3, 0), (50, 150, 50)),
    # body (orange)
    ((1, 1), (255, 120, 0)), ((2, 1), (255, 120, 0)), ((3, 1), (255, 120, 0)),
    ((4, 1), (255, 120, 0)), ((5, 1), (255, 120, 0)),
    ((0, 2), (255, 120, 0)), ((1, 2), (255, 120, 0)), ((2, 2), (255, 120, 0)),
    ((3, 2), (255, 120, 0)), ((4, 2), (255, 120, 0)), ((5, 2), (255, 120, 0)),
    ((6, 2), (255, 120, 0)),
    ((0, 3), (255, 120, 0)), ((1, 3), (255, 120, 0)), ((2, 3), (255, 120, 0)),
    ((3, 3), (255, 120, 0)), ((4, 3), (255, 120, 0)), ((5, 3), (255, 120, 0)),
    ((6, 3), (255, 120, 0)),
    ((1, 4), (255, 120, 0)), ((2, 4), (255, 120, 0)), ((3, 4), (255, 120, 0)),
    ((4, 4), (255, 120, 0)), ((5, 4), (255, 120, 0)),
    # face (black/yellow for eyes)
    ((1, 2), (200, 200, 50)), ((2, 3), (200, 200, 50)),  # left eye
    ((4, 2), (200, 200, 50)), ((5, 3), (200, 200, 50)),  # right eye
    ((3, 4), (200, 200, 50)),  # nose/mouth hint
]

# ghost sprite (5x6)
GHOST_BASE = [
    (1, 0), (2, 0), (3, 0),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
    (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (0, 5), (2, 5), (4, 5),  # wavy bottom
]


class Ghost:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(-10, 70)
        self.y = random.uniform(2, 20)
        self.speed = random.uniform(0.2, 0.5)
        self.direction = random.choice([-1, 1])
        self.float_phase = random.uniform(0, math.pi * 2)
        self.alpha = random.uniform(0.5, 1.0)


class Bat:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(-5, 70)
        self.y = random.uniform(0, 15)
        self.speed = random.uniform(0.5, 1.0)
        self.direction = random.choice([-1, 1])
        self.wing_phase = random.uniform(0, math.pi * 2)


class HalloweenScene(object):
    def __init__(self):
        super().__init__()
        self._ghosts = [Ghost() for _ in range(3)]
        self._bats = [Bat() for _ in range(5)]
        self._last_halloween_pixels = []
        self._halloween_phase = 0

    def _is_halloween(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("halloween", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "10-31"

    @Animator.KeyFrame.add(1)
    def halloween(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_halloween_pixels:
                for px, py in self._last_halloween_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_halloween_pixels = []
            return

        if not self._is_halloween():
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        # clear previous
        for px, py in self._last_halloween_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._halloween_phase += 0.1

        # draw purple/orange gradient sky at top
        for y in range(8):
            intensity = 1 - (y / 8)
            for x in range(64):
                # alternating purple/orange glow
                if (x + int(self._halloween_phase * 2)) % 20 < 10:
                    r, g, b = int(80 * intensity), int(20 * intensity), int(80 * intensity)
                else:
                    r, g, b = int(50 * intensity), int(20 * intensity), int(10 * intensity)
                if r > 0 or g > 0 or b > 0:
                    self.canvas.SetPixel(x, y, r, g, b)
                    drawn_pixels.append((x, y))

        # draw pumpkin in corner
        pumpkin_x = 2
        pumpkin_y = 25
        for (dx, dy), (r, g, b) in PUMPKIN_PIXELS:
            px = pumpkin_x + dx
            py = pumpkin_y + dy
            if 0 <= px < 64 and 0 <= py < 32:
                self.canvas.SetPixel(px, py, r, g, b)
                drawn_pixels.append((px, py))

        # draw floating ghosts
        for ghost in self._ghosts:
            ghost.x += ghost.speed * ghost.direction
            ghost.float_phase += 0.1
            float_offset = math.sin(ghost.float_phase) * 2

            # wrap around
            if ghost.x > 70:
                ghost.x = -10
            elif ghost.x < -10:
                ghost.x = 70

            gy = ghost.y + float_offset
            intensity = int(200 * ghost.alpha)
            for dx, dy in GHOST_BASE:
                px = int(ghost.x + dx)
                py = int(gy + dy)
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, intensity, intensity, intensity)
                    drawn_pixels.append((px, py))

            # ghost eyes (black)
            for ex, ey in [(1, 2), (3, 2)]:
                px = int(ghost.x + ex)
                py = int(gy + ey)
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, 0, 0, 0)

        # draw bats
        for bat in self._bats:
            bat.x += bat.speed * bat.direction
            bat.wing_phase += 0.3

            if bat.x > 70:
                bat.x = -5
            elif bat.x < -5:
                bat.x = 70

            # simple bat: body + wings that flap
            wing_up = math.sin(bat.wing_phase) > 0
            bx, by = int(bat.x), int(bat.y)

            # body
            if 0 <= bx < 64 and 0 <= by < 32:
                self.canvas.SetPixel(bx, by, 30, 30, 40)
                drawn_pixels.append((bx, by))

            # wings
            wing_y = by - 1 if wing_up else by
            for wx in [-1, 1]:
                px = bx + wx
                if 0 <= px < 64 and 0 <= wing_y < 32:
                    self.canvas.SetPixel(px, wing_y, 30, 30, 40)
                    drawn_pixels.append((px, wing_y))

        # "BOO!" text
        boo_x = 50
        boo_pulse = 0.6 + 0.4 * math.sin(self._halloween_phase * 2)
        text_color = graphics.Color(
            int(255 * boo_pulse),
            int(100 * boo_pulse),
            0
        )
        graphics.DrawText(self.canvas, fonts.extrasmall, boo_x, 30, text_color, "BOO!")
        for x in range(boo_x, min(64, boo_x + 20)):
            for y in range(24, 32):
                drawn_pixels.append((x, y))

        self._last_halloween_pixels = drawn_pixels
