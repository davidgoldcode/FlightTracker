import math
from utilities.animator import Animator


def _is_demo_mode():
    try:
        from config import WINDOW_BEARING
        return False
    except (ImportError, NameError):
        return True


DEMO_MODE = _is_demo_mode()

# load window view config
try:
    from config import WINDOW_BEARING, WINDOW_FOV
except (ModuleNotFoundError, NameError, ImportError):
    WINDOW_BEARING = None
    WINDOW_FOV = None

# demo defaults for test_animation.py
DEMO_WINDOW_BEARING = 250
DEMO_WINDOW_FOV = 120

# arrow color (cyan, distinct from pink plane text and green bar)
ARROW_R, ARROW_G, ARROW_B = 0, 160, 160


class BearingIndicatorScene(object):
    def __init__(self):
        super().__init__()
        self._bearing_pixels = []
        self._demo_bearing_phase = 0

    def _get_window_config(self):
        """Get window bearing and FOV, using demo defaults if needed."""
        if DEMO_MODE:
            return DEMO_WINDOW_BEARING, DEMO_WINDOW_FOV
        if WINDOW_BEARING is None or WINDOW_FOV is None:
            return None, None
        return WINDOW_BEARING, WINDOW_FOV

    def _bearing_to_x(self, bearing, window_bearing, window_fov):
        """Map compass bearing to x position (0-63) within window FOV."""
        fov_left = (window_bearing - window_fov / 2) % 360
        diff = (bearing - fov_left + 360) % 360
        fraction = diff / window_fov
        return max(0, min(63, int(fraction * 63)))

    @Animator.KeyFrame.add(1)
    def position_arrow(self, count):
        """Draw small arrow at bottom showing where to look for the current flight.

        Method named 'position_arrow' to sort after 'plane_details' in dir()
        so it draws after the plane scene clears its background region.
        """
        # clear previous
        for px, py in self._bearing_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)
        self._bearing_pixels = []

        # skip during plane intro
        if hasattr(self, 'is_intro_active') and self.is_intro_active():
            return

        window_bearing, window_fov = self._get_window_config()
        if window_bearing is None:
            return

        if DEMO_MODE:
            # sweep arrow across display for visual demo
            self._demo_bearing_phase += 0.03
            sweep = math.sin(self._demo_bearing_phase)
            bearing = window_bearing + sweep * (window_fov / 2) * 0.8
        else:
            if len(self._data) == 0:
                return
            bearing = self._data[self._data_index].get("bearing")
            if bearing is None:
                return

        x = self._bearing_to_x(bearing, window_bearing, window_fov)
        drawn = []

        # small upward-pointing triangle at bottom of display
        # tip at y=30 (may overlap with plane text baseline, that's fine)
        if 0 <= x < 64:
            self.canvas.SetPixel(x, 30, ARROW_R, ARROW_G, ARROW_B)
            drawn.append((x, 30))

        # base at y=31 (3px wide, always visible below plane text)
        for dx in (-1, 0, 1):
            px = x + dx
            if 0 <= px < 64:
                self.canvas.SetPixel(px, 31, ARROW_R, ARROW_G, ARROW_B)
                drawn.append((px, 31))

        self._bearing_pixels = drawn
