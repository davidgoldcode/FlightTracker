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

# marker at y=13: gap row between journey (y=0-12) and flight details (y=14+)
MARKER_Y = 13

# gradient brightness: center bright, edges taper off
MARKER_COLORS = [
    (0, 60, 60),    # outer dim
    (0, 130, 130),  # mid
    (0, 200, 200),  # center bright
    (0, 130, 130),  # mid
    (0, 60, 60),    # outer dim
]


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
        """Draw bearing marker in the gap between journey and flight details.

        Method named 'position_arrow' so it sorts after 'plane_details' in dir().
        Draws at y=13 which is untouched by all other scenes.
        """
        # skip during plane intro
        if hasattr(self, 'is_intro_active') and self.is_intro_active():
            return

        window_bearing, window_fov = self._get_window_config()
        if window_bearing is None:
            return

        if DEMO_MODE:
            # sweep marker across display for visual demo
            self._demo_bearing_phase += 0.03
            sweep = math.sin(self._demo_bearing_phase)
            bearing = window_bearing + sweep * (window_fov / 2) * 0.8
        else:
            if len(self._data) == 0:
                # clear leftover marker when flights disappear
                for px, py in self._bearing_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._bearing_pixels = []
                return
            bearing = self._data[self._data_index].get("bearing")
            if bearing is None:
                return

        # clear previous marker
        for px, py in self._bearing_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        x = self._bearing_to_x(bearing, window_bearing, window_fov)
        drawn = []

        # draw 5px wide gradient marker at y=13
        half = len(MARKER_COLORS) // 2
        for i, (r, g, b) in enumerate(MARKER_COLORS):
            px = x + (i - half)
            if 0 <= px < 64:
                self.canvas.SetPixel(px, MARKER_Y, r, g, b)
                drawn.append((px, MARKER_Y))

        self._bearing_pixels = drawn
