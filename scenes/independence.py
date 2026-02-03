import math
import random
from datetime import datetime
from utilities.animator import Animator
from setup import colours, frames, fonts
from rgbmatrix import graphics


def _is_demo_mode():
    try:
        from config import HOLIDAYS
        return False
    except (ImportError, NameError):
        return True

DEMO_MODE = _is_demo_mode()


class Firework:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(10, 54)
        self.y = random.randint(5, 15)
        self.particles = []
        self.age = 0
        self.max_age = random.randint(20, 35)
        self.color_type = random.choice(['red', 'white', 'blue'])
        self.exploded = False
        self.launch_y = 31
        self.launch_speed = random.uniform(0.8, 1.2)

    def get_color(self):
        if self.color_type == 'red':
            return (255, 50, 50)
        elif self.color_type == 'white':
            return (255, 255, 255)
        else:
            return (50, 50, 255)

    def explode(self):
        self.exploded = True
        color = self.get_color()
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            speed = random.uniform(0.5, 1.5)
            self.particles.append({
                'x': float(self.x),
                'y': float(self.y),
                'vx': math.cos(rad) * speed,
                'vy': math.sin(rad) * speed,
                'color': color,
                'life': random.randint(10, 20)
            })


class Star:
    def __init__(self):
        self.x = random.randint(0, 63)
        self.y = random.randint(0, 12)
        self.brightness = random.uniform(0.3, 1.0)
        self.twinkle_speed = random.uniform(0.1, 0.2)
        self.phase = random.uniform(0, math.pi * 2)


class IndependenceScene(object):
    def __init__(self):
        super().__init__()
        self._fireworks = [Firework() for _ in range(4)]
        self._stars = [Star() for _ in range(20)]
        self._last_independence_pixels = []
        self._phase = 0

    def _is_independence_day(self):
        if DEMO_MODE:
            return True
        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("independence_day", False):
                return False
        except (ImportError, NameError):
            return False
        today = datetime.now().strftime("%m-%d")
        return today == "07-04"

    @Animator.KeyFrame.add(1)
    def independence(self, count):
        if len(self._data):
            if self._last_independence_pixels:
                for px, py in self._last_independence_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_independence_pixels = []
            return

        if not self._is_independence_day():
            return

        drawn_pixels = []

        for px, py in self._last_independence_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self._phase += 0.1

        # dark blue sky background
        for y in range(32):
            for x in range(64):
                self.canvas.SetPixel(x, y, 5, 5, 20)
                drawn_pixels.append((x, y))

        # twinkling stars
        for star in self._stars:
            star.phase += star.twinkle_speed
            brightness = star.brightness * (0.5 + 0.5 * math.sin(star.phase))
            if brightness > 0.3:
                c = int(200 * brightness)
                self.canvas.SetPixel(star.x, star.y, c, c, c)

        # process fireworks
        for fw in self._fireworks:
            if not fw.exploded:
                # launching
                if fw.launch_y > fw.y:
                    fw.launch_y -= fw.launch_speed
                    py = int(fw.launch_y)
                    if 0 <= py < 32:
                        self.canvas.SetPixel(fw.x, py, 255, 200, 100)
                        drawn_pixels.append((fw.x, py))
                else:
                    fw.explode()
            else:
                # exploded - animate particles
                fw.age += 1
                if fw.age > fw.max_age:
                    fw.reset()
                    continue

                for particle in fw.particles:
                    if particle['life'] <= 0:
                        continue

                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    particle['vy'] += 0.05  # gravity
                    particle['life'] -= 1

                    px, py = int(particle['x']), int(particle['y'])
                    if 0 <= px < 64 and 0 <= py < 32:
                        fade = particle['life'] / 20.0
                        r, g, b = particle['color']
                        r = int(r * fade)
                        g = int(g * fade)
                        b = int(b * fade)
                        self.canvas.SetPixel(px, py, r, g, b)
                        drawn_pixels.append((px, py))

        # red/white/blue stripes at bottom
        stripe_height = 3
        for x in range(64):
            for dy in range(stripe_height):
                y = 29 + dy
                if y < 32:
                    if dy == 0:
                        self.canvas.SetPixel(x, y, 255, 50, 50)  # red
                    elif dy == 1:
                        self.canvas.SetPixel(x, y, 255, 255, 255)  # white
                    else:
                        self.canvas.SetPixel(x, y, 50, 50, 255)  # blue
                    drawn_pixels.append((x, y))

        # "USA!" text with wave
        text = "USA!"
        wave_offset = int(math.sin(self._phase * 3) * 2)
        text_colors = [
            graphics.Color(255, 50, 50),   # red
            graphics.Color(255, 255, 255), # white
            graphics.Color(50, 50, 255),   # blue
            graphics.Color(255, 200, 50),  # gold !
        ]
        x_start = (64 - len(text) * 6) // 2
        for i, char in enumerate(text):
            char_wave = int(math.sin(self._phase * 3 + i * 0.5) * 1)
            graphics.DrawText(self.canvas, fonts.extrasmall, x_start + i * 6, 24 + char_wave, text_colors[i % len(text_colors)], char)

        for tx in range(max(0, x_start), min(64, x_start + len(text) * 6)):
            for ty in range(18, 26):
                drawn_pixels.append((tx, ty))

        self._last_independence_pixels = drawn_pixels
