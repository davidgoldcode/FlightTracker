import math
import random
from datetime import datetime, date
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

# chinese new year dates (first day of lunar new year)
CHINESE_NEW_YEAR_DATES = {
    2024: (2, 10),
    2025: (1, 29),
    2026: (2, 17),
    2027: (2, 6),
    2028: (1, 26),
    2029: (2, 13),
    2030: (2, 3),
    2031: (1, 23),
    2032: (2, 11),
    2033: (1, 31),
    2034: (2, 19),
    2035: (2, 8),
}

# zodiac animals by year
ZODIAC = {
    2024: "Dragon",
    2025: "Snake",
    2026: "Horse",
    2027: "Goat",
    2028: "Monkey",
    2029: "Rooster",
    2030: "Dog",
    2031: "Pig",
    2032: "Rat",
    2033: "Ox",
    2034: "Tiger",
    2035: "Rabbit",
}


class Lantern:
    def __init__(self, x):
        self.x = x
        self.base_y = random.randint(3, 8)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.05, 0.1)
        self.size = random.choice([1, 2])


class Firework:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(5, 59)
        self.y = random.randint(8, 18)
        self.particles = []
        self.age = 0
        self.max_age = random.randint(15, 25)
        self.exploded = False
        self.launch_y = 31
        self.launch_speed = random.uniform(1.0, 1.5)

    def explode(self):
        self.exploded = True
        gold = (255, 200, 50)
        red = (255, 50, 50)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            speed = random.uniform(0.5, 1.0)
            color = random.choice([gold, red])
            self.particles.append({
                'x': float(self.x),
                'y': float(self.y),
                'vx': math.cos(rad) * speed,
                'vy': math.sin(rad) * speed,
                'color': color,
                'life': random.randint(8, 15)
            })


class ChineseNewYearScene(object):
    def __init__(self):
        super().__init__()
        self._lanterns = [Lantern(x * 12 + 6) for x in range(5)]
        self._cny_fireworks = [Firework() for _ in range(2)]
        self._last_cny_pixels = []
        self._cny_phase = 0

    def _get_cny_info(self):
        """Return (is_cny, zodiac_animal) or (False, None)."""
        if DEMO_MODE:
            return True, "Dragon"

        try:
            from config import HOLIDAYS
            if not HOLIDAYS.get("chinese_new_year", False):
                return False, None
        except (ImportError, NameError):
            return False, None

        today = date.today()
        year = today.year

        if year not in CHINESE_NEW_YEAR_DATES:
            return False, None

        month, day = CHINESE_NEW_YEAR_DATES[year]
        cny_date = date(year, month, day)

        # celebrate for a few days
        delta = (today - cny_date).days
        if 0 <= delta <= 2:
            return True, ZODIAC.get(year, "")

        return False, None

    def _draw_lantern(self, drawn_pixels, x, y, size):
        """Draw a Chinese lantern."""
        red = (220, 30, 30)
        gold = (255, 200, 50)
        dark_red = (150, 20, 20)

        if size == 1:
            # small lantern
            points = [(0, 0), (0, 1), (0, 2)]
            for dx, dy in points:
                px, py = x + dx, y + dy
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, *red)
                    drawn_pixels.append((px, py))
            # gold tassle
            if 0 <= x < 64 and 0 <= y + 3 < 32:
                self.canvas.SetPixel(x, y + 3, *gold)
                drawn_pixels.append((x, y + 3))
        else:
            # larger lantern
            body = [
                (-1, 0), (0, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1),
                (-1, 2), (0, 2), (1, 2),
                (0, 3),
            ]
            for dx, dy in body:
                px, py = x + dx, y + dy
                if 0 <= px < 64 and 0 <= py < 32:
                    self.canvas.SetPixel(px, py, *red)
                    drawn_pixels.append((px, py))
            # gold bands
            for dx in [-1, 0, 1]:
                px = x + dx
                if 0 <= px < 64:
                    if 0 <= y < 32:
                        self.canvas.SetPixel(px, y, *gold)
                    if 0 <= y + 2 < 32:
                        self.canvas.SetPixel(px, y + 2, *gold)
            # tassle
            if 0 <= x < 64 and 0 <= y + 4 < 32:
                self.canvas.SetPixel(x, y + 4, *gold)
                drawn_pixels.append((x, y + 4))

        # string
        if 0 <= x < 64 and 0 <= y - 1 < 32:
            self.canvas.SetPixel(x, y - 1, *dark_red)
            drawn_pixels.append((x, y - 1))

    @Animator.KeyFrame.add(1)
    def chinese_new_year(self, count):
        if len(self._data):
            if self._last_cny_pixels:
                for px, py in self._last_cny_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_cny_pixels = []
            return

        is_cny, zodiac = self._get_cny_info()
        if not is_cny:
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        drawn_pixels = []

        for px, py in self._last_cny_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)

        self._cny_phase += 0.1

        # red background with subtle pattern (below clock area)
        for y in range(11, 32):
            for x in range(64):
                intensity = 0.2 + 0.05 * math.sin(self._cny_phase * 0.5 + x * 0.1 + y * 0.1)
                r = int(200 * intensity)
                g = int(30 * intensity)
                b = int(30 * intensity)
                self.canvas.SetPixel(x, y, r, g, b)
                drawn_pixels.append((x, y))

        # draw lanterns with sway
        for lantern in self._lanterns:
            lantern.sway_phase += lantern.sway_speed
            sway_x = int(lantern.x + math.sin(lantern.sway_phase) * 1)
            self._draw_lantern(drawn_pixels, sway_x, lantern.base_y, lantern.size)

        # fireworks
        for fw in self._cny_fireworks:
            if not fw.exploded:
                if fw.launch_y > fw.y:
                    fw.launch_y -= fw.launch_speed
                    py = int(fw.launch_y)
                    if 0 <= py < 32:
                        self.canvas.SetPixel(fw.x, py, 255, 200, 100)
                        drawn_pixels.append((fw.x, py))
                else:
                    fw.explode()
            else:
                fw.age += 1
                if fw.age > fw.max_age:
                    fw.reset()
                    continue

                for particle in fw.particles:
                    if particle['life'] <= 0:
                        continue

                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    particle['vy'] += 0.03
                    particle['life'] -= 1

                    px, py = int(particle['x']), int(particle['y'])
                    if 0 <= px < 64 and 0 <= py < 32:
                        fade = particle['life'] / 15.0
                        r, g, b = particle['color']
                        self.canvas.SetPixel(px, py, int(r * fade), int(g * fade), int(b * fade))
                        drawn_pixels.append((px, py))

        # zodiac text at bottom
        text = f"Year of {zodiac}"
        pulse = 0.7 + 0.3 * math.sin(self._cny_phase * 2)
        text_color = graphics.Color(int(255 * pulse), int(200 * pulse), int(50 * pulse))
        x = (64 - len(text) * 4) // 2
        graphics.DrawText(self.canvas, fonts.extrasmall, x, 28, text_color, text)
        for tx in range(max(0, x), min(64, x + len(text) * 5)):
            for ty in range(22, 30):
                drawn_pixels.append((tx, ty))

        self._last_cny_pixels = drawn_pixels
