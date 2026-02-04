"""
Plane sweep animation that plays when a new flight is detected.
Shows a commercial airliner flying across screen - fills full height.
"""
from utilities.animator import Animator
from setup import colours, frames


class PlaneIntroScene(object):
    def __init__(self):
        super().__init__()
        self._plane_intro_active = False
        self._plane_intro_x = -50
        self._plane_intro_frames = 0
        self._had_no_flights = True

    def trigger_plane_intro(self):
        """Call this when new flight data arrives after having no flights."""
        self._plane_intro_active = True
        self._plane_intro_x = -50
        self._plane_intro_frames = 0

    def _set_pixel(self, px, py, color):
        """Helper to set pixel if in bounds."""
        px, py = int(px), int(py)
        if 0 <= px < 64 and 0 <= py < 32:
            self.canvas.SetPixel(px, py, *color)

    def _draw_plane(self, x):
        """Draw Boeing 777 style plane - full screen height (32px)."""
        # colors
        white = (240, 240, 245)
        light_gray = (200, 200, 210)
        dark_gray = (120, 120, 130)
        blue = (30, 60, 180)
        red = (200, 40, 50)
        window_blue = (60, 90, 140)
        engine_gray = (180, 180, 185)

        # plane spans full 32 pixel height
        # y=0 is top, y=31 is bottom
        # center of fuselage at y=16

        # fuselage - fill it row by row for smooth shape
        # top taper (rows 0-5)
        for dx in range(18, 28):
            self._set_pixel(x + dx, 0, white)
        for dx in range(14, 32):
            self._set_pixel(x + dx, 1, white)
        for dx in range(10, 36):
            self._set_pixel(x + dx, 2, white)
        for dx in range(7, 39):
            self._set_pixel(x + dx, 3, white)
        for dx in range(5, 41):
            self._set_pixel(x + dx, 4, white)
        for dx in range(3, 43):
            self._set_pixel(x + dx, 5, white)

        # upper body (rows 6-11)
        for dy in range(6, 12):
            for dx in range(1, 45):
                self._set_pixel(x + dx, dy, white)

        # blue stripe (rows 12-14)
        for dy in range(12, 15):
            for dx in range(0, 46):
                self._set_pixel(x + dx, dy, blue)

        # red stripe (rows 15-17)
        for dy in range(15, 18):
            for dx in range(0, 46):
                self._set_pixel(x + dx, dy, red)

        # lower body (rows 18-23)
        for dy in range(18, 24):
            for dx in range(1, 45):
                self._set_pixel(x + dx, dy, white)

        # bottom taper (rows 24-31)
        for dx in range(3, 43):
            self._set_pixel(x + dx, 24, white)
        for dx in range(5, 41):
            self._set_pixel(x + dx, 25, white)
        for dx in range(7, 39):
            self._set_pixel(x + dx, 26, white)
        for dx in range(10, 36):
            self._set_pixel(x + dx, 27, white)
        for dx in range(14, 32):
            self._set_pixel(x + dx, 28, white)
        for dx in range(18, 28):
            self._set_pixel(x + dx, 29, white)

        # nose cone (right side, rounded)
        for dy in range(4, 26):
            self._set_pixel(x + 46, dy, light_gray)
        for dy in range(5, 25):
            self._set_pixel(x + 47, dy, light_gray)
        for dy in range(7, 23):
            self._set_pixel(x + 48, dy, light_gray)
        for dy in range(9, 21):
            self._set_pixel(x + 49, dy, light_gray)
        for dy in range(12, 18):
            self._set_pixel(x + 50, dy, light_gray)

        # cockpit windows (dark area on nose)
        for dy in range(4, 9):
            for dx in range(42, 47):
                self._set_pixel(x + dx, dy, window_blue)

        # passenger windows (row of dots)
        for dx in range(10, 40, 4):
            self._set_pixel(x + dx, 7, window_blue)
            self._set_pixel(x + dx + 1, 7, window_blue)
            self._set_pixel(x + dx, 8, window_blue)
            self._set_pixel(x + dx + 1, 8, window_blue)

        # tail fin (vertical stabilizer) - at back, going up
        for dy in range(-12, 6):
            for dx in range(-2, 4):
                self._set_pixel(x + dx, dy, white)
        for dy in range(-10, 4):
            for dx in range(4, 7):
                self._set_pixel(x + dx, dy, white)

        # tail blue stripe
        for dy in range(-10, 2):
            self._set_pixel(x + 0, dy, blue)
            self._set_pixel(x + 1, dy, blue)
            self._set_pixel(x + 2, dy, blue)

        # engine (underneath, larger)
        for dy in range(26, 32):
            for dx in range(18, 30):
                self._set_pixel(x + dx, dy, engine_gray)

        # engine intake (dark circle at front of engine)
        for dy in range(27, 31):
            self._set_pixel(x + 30, dy, dark_gray)
            self._set_pixel(x + 31, dy, dark_gray)

    def _is_demo_mode(self):
        """Check if running in test/demo mode (test_animation.py)."""
        # demo mode only when overhead doesn't exist (test harness)
        # NOT when overhead exists but has no data (that's just idle mode)
        return not hasattr(self, 'overhead') or self.overhead is None

    @Animator.KeyFrame.add(1)
    def plane_intro(self, count):
        demo_mode = self._is_demo_mode()

        if demo_mode:
            # in test_animation.py - loop the intro for demo purposes
            if not self._plane_intro_active and self._plane_intro_x > 70:
                if count % 30 == 0:
                    self.trigger_plane_intro()
            elif not self._plane_intro_active:
                self.trigger_plane_intro()
        else:
            # production mode - only trigger on flight detection
            has_flights_now = len(self._data) > 0
            if not has_flights_now:
                self._had_no_flights = True
            if self._had_no_flights and has_flights_now and not self._plane_intro_active:
                self.trigger_plane_intro()
                self._had_no_flights = False

        if not self._plane_intro_active:
            return

        # the plane acts as a "wipe" transition
        # left of plane = black (cleared for flight info after intro)
        # right of plane = sky background
        plane_back_x = self._plane_intro_x - 2  # trailing edge of plane

        for py in range(32):
            for px in range(64):
                if px < plane_back_x:
                    # left side: clear to black
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                else:
                    # right side: sky gradient
                    blue_val = 220 - int(py * 1.5)
                    green_val = 240 - int(py * 2)
                    self.canvas.SetPixel(px, py, 135 - py, green_val, 255)

        # draw the plane (no preview - let real scenes render after intro ends)
        self._draw_plane(self._plane_intro_x)

        # move plane
        self._plane_intro_x += 3
        self._plane_intro_frames += 1

        # end animation when plane fully exits
        if self._plane_intro_x > 70:
            self._plane_intro_active = False

    def is_intro_active(self):
        """Check if intro animation is currently playing."""
        return self._plane_intro_active
