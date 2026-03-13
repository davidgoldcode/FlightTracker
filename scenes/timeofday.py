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

# time periods and their color schemes
# format: (hour_start, hour_end, sky_colors, ground_color)
TIME_PERIODS = {
    "night": (0, 5, [(0, 0, 30), (0, 0, 50), (10, 10, 40)], (20, 20, 30)),
    "dawn": (5, 7, [(255, 150, 100), (255, 200, 150), (100, 150, 200)], (40, 60, 40)),
    "morning": (7, 10, [(100, 180, 255), (150, 200, 255), (200, 220, 255)], (60, 120, 60)),
    "midday": (10, 14, [(80, 150, 255), (120, 180, 255), (180, 210, 255)], (80, 140, 80)),
    "afternoon": (14, 17, [(100, 170, 255), (140, 190, 255), (180, 210, 255)], (70, 130, 70)),
    "sunset": (17, 20, [(255, 100, 50), (255, 150, 80), (200, 100, 150)], (50, 80, 50)),
    "dusk": (20, 22, [(80, 50, 120), (100, 70, 150), (50, 40, 100)], (30, 40, 50)),
    "night_late": (22, 24, [(0, 0, 30), (0, 0, 50), (10, 10, 40)], (20, 20, 30)),
}


class TimeOfDayScene(object):
    def __init__(self):
        super().__init__()
        self._last_tod_pixels = []
        self._sun_moon_phase = 0

    def _get_period(self):
        hour = get_now().hour
        for name, (start, end, colors, ground) in TIME_PERIODS.items():
            if start <= hour < end:
                return name, colors, ground
        return "night", TIME_PERIODS["night"][2], TIME_PERIODS["night"][3]

    def _interpolate_color(self, color1, color2, t):
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        return (r, g, b)

    @Animator.KeyFrame.add(2)  # slower update rate
    def time_of_day(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_tod_pixels:
                for px, py in self._last_tod_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_tod_pixels = []
            return

        # only show in demo/test mode
        if not DEMO_MODE:
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []
        self._sun_moon_phase += 0.05

        # clear previous
        for px, py in self._last_tod_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        period, sky_colors, ground_color = self._get_period()
        hour = get_now().hour

        # draw sky gradient
        for y in range(24):
            # determine which colors to blend
            t = y / 24
            if t < 0.5:
                c1, c2 = sky_colors[0], sky_colors[1]
                blend_t = t * 2
            else:
                c1, c2 = sky_colors[1], sky_colors[2]
                blend_t = (t - 0.5) * 2

            r, g, b = self._interpolate_color(c1, c2, blend_t)

            for x in range(64):
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        # draw sun or moon based on time
        if 6 <= hour < 20:
            # sun (yellow/orange circle)
            sun_x = 50
            sun_y = 8 + int(4 * math.sin(self._sun_moon_phase * 0.2))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx * dx + dy * dy <= 9:  # circle
                        px = sun_x + dx
                        py = sun_y + dy
                        if 0 <= px < 64 and 0 <= py < 32:
                            # gradient from center
                            dist = math.sqrt(dx * dx + dy * dy)
                            intensity = 1 - dist / 4
                            r = int(255 * intensity)
                            g = int(220 * intensity)
                            b = int(100 * intensity)
                            self.canvas.SetPixel(px, py, r, g, b)
        else:
            # moon (white/gray crescent)
            moon_x = 50
            moon_y = 8
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    dist_main = dx * dx + dy * dy
                    dist_shadow = (dx + 1) * (dx + 1) + dy * dy
                    if dist_main <= 9 and dist_shadow > 6:  # crescent
                        px = moon_x + dx
                        py = moon_y + dy
                        if 0 <= px < 64 and 0 <= py < 32:
                            self.canvas.SetPixel(px, py, 230, 230, 200)

            # stars at night
            if period in ("night", "night_late", "dusk"):
                for i in range(15):
                    star_x = (i * 7 + int(self._sun_moon_phase)) % 64
                    star_y = (i * 3) % 20
                    twinkle = 0.5 + 0.5 * math.sin(self._sun_moon_phase + i)
                    brightness = int(150 * twinkle)
                    self.canvas.SetPixel(star_x, star_y, brightness, brightness, brightness)
                    drawn_pixels.append((star_x, star_y))

        # draw ground/horizon
        for x in range(64):
            for y in range(24, 32):
                # gradient from ground color to darker
                t = (y - 24) / 8
                r = int(ground_color[0] * (1 - t * 0.3))
                g = int(ground_color[1] * (1 - t * 0.3))
                b = int(ground_color[2] * (1 - t * 0.3))
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        self._last_tod_pixels = drawn_pixels
