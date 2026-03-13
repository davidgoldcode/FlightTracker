import random
import time
import json
import urllib.request
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

# morning hours when snow animation can show
MORNING_START = 5
MORNING_END = 10

# weather check cache
_weather_cache = {"is_snowing": False, "checked_at": 0}
WEATHER_CACHE_SECONDS = 1800  # 30 minutes


def _check_snow_from_api():
    """Query OpenWeather API for snow conditions."""
    try:
        from config import WEATHER_LOCATION, OPENWEATHER_API_KEY
        if not OPENWEATHER_API_KEY:
            return _check_snow_from_temperature()

        url = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + WEATHER_LOCATION
            + "&appid="
            + OPENWEATHER_API_KEY
            + "&units=metric"
        )
        request = urllib.request.Request(url)
        raw_data = urllib.request.urlopen(request, timeout=3).read()
        data = json.loads(raw_data.decode("utf-8"))

        for condition in data.get("weather", []):
            if condition.get("main", "").lower() == "snow":
                return True
        return False

    except Exception:
        return _check_snow_from_temperature()


def _check_snow_from_temperature():
    """Temperature-based heuristic for snow (fallback when no API key)."""
    try:
        from scenes.weather import grab_current_temperature
        from config import WEATHER_LOCATION
        temp = grab_current_temperature(WEATHER_LOCATION, "metric")
        return temp is not None and temp <= 2
    except Exception:
        return False


def _is_snowy_morning():
    """Check if it's morning and weather reports snow."""
    now = get_now()
    if not (MORNING_START <= now.hour < MORNING_END):
        return False

    # use cached result if fresh enough
    if time.time() - _weather_cache["checked_at"] < WEATHER_CACHE_SECONDS:
        return _weather_cache["is_snowing"]

    # refresh cache
    _weather_cache["is_snowing"] = _check_snow_from_api()
    _weather_cache["checked_at"] = time.time()
    return _weather_cache["is_snowing"]


# snow settings
NUM_SNOWFLAKES = 50
WIND_DRIFT = 0.3  # horizontal drift


class Snowflake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-10, 0)  # start above screen
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.choice([1, 1, 1, 2])  # mostly small
        self.brightness = random.randint(180, 255)
        self.drift = random.uniform(-WIND_DRIFT, WIND_DRIFT)


class FallingSnowScene(object):
    def __init__(self):
        super().__init__()
        self._fallingsnow_flakes = []
        self._snow_initialized = False
        self._last_snow_pixels = []
        self._snow_accumulation = [0] * 64  # snow buildup at bottom

    def _init_snow(self):
        self._fallingsnow_flakes = [Snowflake() for _ in range(NUM_SNOWFLAKES)]
        # spread initial snowflakes across screen
        for i, flake in enumerate(self._fallingsnow_flakes):
            flake.y = random.uniform(0, 31)
        self._snow_initialized = True

    @Animator.KeyFrame.add(1)  # run every frame for smooth falling
    def falling_snow(self, count):
        # only show when no flights overhead
        if len(self._data):
            # clear snow if flights appear
            if self._last_snow_pixels:
                for px, py in self._last_snow_pixels:
                    self.canvas.SetPixel(px, py, 0, 0, 0)
                self._last_snow_pixels = []
            return

        # only show on snowy mornings (or always in demo mode)
        if not DEMO_MODE and not _is_snowy_morning():
            return

        # love messages take priority when active
        if getattr(self, '_msg_active', False):
            return

        # mutual exclusion - only one idle animation per frame
        if self._idle_drawn_this_frame:
            return
        self._idle_drawn_this_frame = True

        # initialize on first run
        if not self._snow_initialized:
            self._init_snow()

        drawn_pixels = []

        # clear previous positions
        for px, py in self._last_snow_pixels:
            self.canvas.SetPixel(px, py, 0, 0, 0)

        self.clear_clock_region(drawn_pixels)

        # update and draw snowflakes
        for flake in self._fallingsnow_flakes:
            # update position
            flake.y += flake.speed
            flake.x += flake.drift + random.uniform(-0.1, 0.1)  # slight random wobble

            # wrap horizontally
            if flake.x < 0:
                flake.x = 63
            elif flake.x > 63:
                flake.x = 0

            # check if landed
            floor_y = 31 - self._snow_accumulation[int(flake.x)]
            if flake.y >= floor_y:
                # accumulate snow (slowly)
                if random.random() < 0.02 and self._snow_accumulation[int(flake.x)] < 5:
                    self._snow_accumulation[int(flake.x)] += 1
                flake.reset()
                continue

            # draw snowflake
            px = int(flake.x)
            py = int(flake.y)
            if 0 <= px < 64 and 0 <= py < 32:
                b = flake.brightness
                self.canvas.SetPixel(px, py, b, b, b)
                drawn_pixels.append((px, py))

                # larger snowflakes
                if flake.size == 2:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < 64 and 0 <= ny < 32:
                            dim = b // 2
                            self.canvas.SetPixel(nx, ny, dim, dim, dim)
                            drawn_pixels.append((nx, ny))

        # draw accumulated snow at bottom
        for x in range(64):
            height = self._snow_accumulation[x]
            for dy in range(height):
                y = 31 - dy
                # slight color variation for texture
                b = 200 + random.randint(-20, 20)
                self.canvas.SetPixel(x, y, b, b, b)
                drawn_pixels.append((x, y))

        # slowly melt accumulated snow
        if random.random() < 0.01:
            x = random.randint(0, 63)
            if self._snow_accumulation[x] > 0:
                self._snow_accumulation[x] -= 1

        self._last_snow_pixels = drawn_pixels
