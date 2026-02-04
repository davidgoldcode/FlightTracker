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

# firework colors
FIREWORK_COLORS = [
    (255, 50, 50),    # red
    (50, 255, 50),    # green
    (50, 50, 255),    # blue
    (255, 255, 50),   # yellow
    (255, 50, 255),   # magenta
    (50, 255, 255),   # cyan
    (255, 150, 50),   # orange
    (255, 255, 255),  # white
]


class Firework:
    def __init__(self):
        self.active = False
        self.particles = []
        self.reset()

    def reset(self):
        self.x = random.uniform(10, 54)
        self.y = random.uniform(5, 15)
        self.color = random.choice(FIREWORK_COLORS)
        self.particles = []
        self.age = 0
        self.active = True

        # create explosion particles
        num_particles = random.randint(8, 16)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 1.5)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
            })

    def update(self):
        if not self.active:
            return

        self.age += 1
        if self.age > 30:
            self.active = False
            return

        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.05  # gravity


class NewYearScene(object):
    def __init__(self):
        super().__init__()
        self._newyear_fireworks = [Firework() for _ in range(5)]
        self._last_newyear_pixels = []
        self._newyear_phase = 0
        self._demo_countdown = 10  # for demo mode

    def _is_new_years_eve(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("new_years", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "12-31"

    def _get_countdown(self):
        """Get seconds until midnight, or None if past midnight."""
        if DEMO_MODE:
            # cycle through countdown for demo
            self._demo_countdown -= 0.1
            if self._demo_countdown < -5:
                self._demo_countdown = 10
            return max(0, int(self._demo_countdown))

        now = datetime.now()
        if now.hour == 23 and now.minute >= 59 and now.second >= 50:
            return 60 - now.second
        elif now.hour == 0 and now.minute == 0 and now.second < 10:
            return 0  # just past midnight, show celebration
        return None  # not countdown time

    @Animator.KeyFrame.add(1)
    def newyear(self, count):
        # only show when no flights overhead
        if len(self._data):
            if self._last_newyear_pixels:
                for px, py in self._last_newyear_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_newyear_pixels = []
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        if not self._is_new_years_eve():
            return

        countdown = self._get_countdown()
        if countdown is None and not DEMO_MODE:
            return

        drawn_pixels = []

        # clear previous
        for px, py in self._last_newyear_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._newyear_phase += 0.15

        if countdown is not None and countdown > 0:
            # countdown mode
            # big number in center
            num_str = str(countdown)
            pulse = 0.6 + 0.4 * math.sin(self._newyear_phase * 3)
            text_color = graphics.Color(
                int(255 * pulse),
                int(255 * pulse),
                int(50 * pulse)
            )
            # center the number
            x = 32 - len(num_str) * 4
            graphics.DrawText(self.canvas, fonts.small, x, 20, text_color, num_str)
            for tx in range(max(0, x), min(64, x + len(num_str) * 8)):
                for ty in range(10, 24):
                    drawn_pixels.append((tx, ty))

            # "Happy New Year" text at top
            msg = "NEW YEAR"
            msg_color = graphics.Color(100, 100, 255)
            mx = (64 - len(msg) * 4) // 2
            graphics.DrawText(self.canvas, fonts.extrasmall, mx, 7, msg_color, msg)
            for tx in range(mx, min(64, mx + len(msg) * 5)):
                for ty in range(1, 9):
                    drawn_pixels.append((tx, ty))

        else:
            # celebration mode - fireworks!
            year = datetime.now().year + 1 if not DEMO_MODE else 2026
            msg = f"HAPPY {year}!"
            pulse = 0.7 + 0.3 * math.sin(self._newyear_phase * 2)
            text_color = graphics.Color(
                int(255 * pulse),
                int(220 * pulse),
                int(50 * pulse)
            )
            x = (64 - len(msg) * 4) // 2
            graphics.DrawText(self.canvas, fonts.extrasmall, x, 20, text_color, msg)
            for tx in range(x, min(64, x + len(msg) * 5)):
                for ty in range(14, 22):
                    drawn_pixels.append((tx, ty))

            # launch/update fireworks
            for fw in self._newyear_fireworks:
                if not fw.active and random.random() < 0.1:
                    fw.reset()

                if fw.active:
                    fw.update()
                    fade = max(0, 1 - fw.age / 30)
                    r, g, b = fw.color
                    r = int(r * fade)
                    g = int(g * fade)
                    b = int(b * fade)

                    for p in fw.particles:
                        px, py = int(p['x']), int(p['y'])
                        if 0 <= px < 64 and 0 <= py < 32:
                            self.canvas.SetPixel(px, py, r, g, b)
                            drawn_pixels.append((px, py))

        self._last_newyear_pixels = drawn_pixels
