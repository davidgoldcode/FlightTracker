import random
import math
from utilities.animator import Animator
from utilities.datenow import get_now
from setup import frames


def _is_demo_mode():
    try:
        from config import ZONE_HOME
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()


def _is_quiet_hours():
    """Check if current time falls within configured quiet hours."""
    now = get_now()

    try:
        from config import QUIET_SCHEDULE
        is_weekend = now.weekday() >= 5
        schedule = QUIET_SCHEDULE.get("weekend" if is_weekend else "weekday", {})

        for period in schedule.values():
            if not isinstance(period, dict) or "start" not in period:
                continue
            start_h, start_m = map(int, period["start"].split(":"))
            end_h, end_m = map(int, period["end"].split(":"))

            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            now_minutes = now.hour * 60 + now.minute

            # handle overnight spans (e.g., 22:00 to 02:00)
            if start_minutes > end_minutes:
                if now_minutes >= start_minutes or now_minutes < end_minutes:
                    return True
            else:
                if start_minutes <= now_minutes < end_minutes:
                    return True

        return False

    except (ImportError, NameError):
        pass

    # legacy config fallback
    try:
        from config import QUIET_HOURS_START, QUIET_HOURS_END
        start_h, start_m = map(int, QUIET_HOURS_START.split(":"))
        end_h, end_m = map(int, QUIET_HOURS_END.split(":"))

        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        now_minutes = now.hour * 60 + now.minute

        if start_minutes > end_minutes:
            return now_minutes >= start_minutes or now_minutes < end_minutes
        else:
            return start_minutes <= now_minutes < end_minutes

    except (ImportError, NameError):
        return False


# fire colors from hottest to coolest
FIRE_COLORS = [
    (255, 255, 220),  # white/yellow (hottest core)
    (255, 220, 80),   # bright yellow
    (255, 180, 20),   # yellow-orange
    (255, 120, 0),    # orange
    (255, 60, 0),     # red-orange
    (200, 30, 0),     # red
    (120, 20, 0),     # dark red
    (60, 10, 0),      # embers
]

# fireplace dimensions
FIRE_WIDTH = 64
FIRE_HEIGHT = 28
FIRE_X_OFFSET = 0
FIRE_Y_OFFSET = 4


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

    @Animator.KeyFrame.add(2)
    def fireplace(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_fire_pixels:
                for px, py in self._last_fire_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_fire_pixels = []
            return

        # only show during quiet hours (or always in demo mode)
        if not DEMO_MODE and not _is_quiet_hours():
            return

        # love messages take priority when active
        if getattr(self, '_msg_active', False):
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        if not self._fire_initialized:
            self._init_fire()

        drawn_pixels = []

        # clear previous
        for px, py in self._last_fire_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)

        # generate intense heat at bottom (fire source)
        for x in range(FIRE_WIDTH):
            # center burns hotter
            center_dist = abs(x - FIRE_WIDTH // 2)
            center_bonus = max(0, 30 - center_dist)

            # base heat with variation
            heat = random.randint(220, 255) + center_bonus
            heat = min(255, heat)

            # occasional cooler spots for flicker
            if random.random() < 0.15:
                heat = random.randint(180, 220)

            self._fire_grid[FIRE_HEIGHT - 1][x] = heat
            # also seed the row above for taller flames
            if random.random() < 0.7:
                self._fire_grid[FIRE_HEIGHT - 2][x] = random.randint(200, 255)

        # propagate fire upward with gentler cooling
        for y in range(FIRE_HEIGHT - 3, -1, -1):
            for x in range(FIRE_WIDTH):
                # sample from below with wind drift
                below_left = self._fire_grid[y + 1][max(0, x - 1)]
                below = self._fire_grid[y + 1][x]
                below_right = self._fire_grid[y + 1][min(FIRE_WIDTH - 1, x + 1)]
                below_far = self._fire_grid[min(FIRE_HEIGHT - 1, y + 2)][x]

                # weighted average favoring center column
                avg = (below_left + below * 3 + below_right + below_far) // 6

                # gentler cooling that increases with height
                height_factor = y / FIRE_HEIGHT  # 0 at bottom, 1 at top
                cooling = random.randint(3, 12) + int(height_factor * 15)

                # add random flicker/turbulence
                if random.random() < 0.1:
                    avg += random.randint(-20, 30)

                self._fire_grid[y][x] = max(0, min(255, avg - cooling))

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
