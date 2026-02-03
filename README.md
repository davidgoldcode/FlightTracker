# Flight Tracker LED

Personal fork of [ColinWaddell/FlightTracker](https://github.com/ColinWaddell/FlightTracker) with custom animations and configuration.

## Credits

Original project by [Colin Waddell](https://blog.colinwaddell.com/flight-tracker/). Licensed under GPL v3.0 - see [LICENSE](LICENSE).

## Hardware

| Component | Model | Link |
| --------- | ----- | ---- |
| Computer | Raspberry Pi 3 B+ | [Adafruit](https://www.adafruit.com/product/3775) |
| Bonnet | Adafruit RGB Matrix Bonnet | [Adafruit](https://www.adafruit.com/product/3211) |
| Display | Waveshare 64x32 P3 LED Matrix (P3-6432-2121-16S) | [Waveshare](https://www.waveshare.com/rgb-matrix-p3-64x32.htm) |
| Power | 5V 4A DC Power Supply | [Adafruit](https://www.adafruit.com/product/1466) |

## Setup

See [original repo](https://github.com/ColinWaddell/FlightTracker) for full installation instructions.

Key flags for this hardware combo (Waveshare panel + Adafruit bonnet + Convenience mode):

```bash
--led-gpio-mapping=adafruit-hat
--led-no-hardware-pulse
--led-slowdown-gpio=4
```

## Example Config

Create `config.py` with your location. Example for NYC area:

```python
# Zone is ~20km box around your location
# Get coordinates from Google Maps (right-click your location)
ZONE_HOME = {
    "tl_y": 40.85,    # lat + 0.1
    "tl_x": -74.10,   # long - 0.1
    "br_y": 40.65,    # lat - 0.1
    "br_x": -73.90    # long + 0.1
}

LOCATION_HOME = [40.75, -74.00, 0.010]  # lat, long, altitude in km

WEATHER_LOCATION = "New York, NY"
BRIGHTNESS = 50
GPIO_SLOWDOWN = 4
MIN_ALTITUDE = 100
TEMPERATURE_UNITS = "imperial"
JOURNEY_CODE_SELECTED = "LGA"  # nearby airport to highlight
JOURNEY_BLANK_FILLER = " ? "
HAT_PWM_ENABLED = False
HARDWARE_PULSE = False
OPENWEATHER_API_KEY = ""  # get free key from openweathermap.org
```

## Custom Features

- 12-hour time format (AM/PM)
- Weather API null-safety fix
- Custom animations (WIP)

## Local Development with Emulator

Test animations on your Mac without hardware using [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator).

### 1. Clone and setup environment

```bash
git clone https://github.com/davidgoldcode/FlightTracker
cd FlightTracker
python3 -m venv env
source env/bin/activate
```

### 2. Install dependencies

The requirements.txt includes `RPi.GPIO` which only works on Raspberry Pi. Install the rest manually:

```bash
pip install beautifulsoup4 requests FlightRadarAPI RGBMatrixEmulator
```

### 3. Create config.py

Copy the example config from above, or create a minimal one:

```python
ZONE_HOME = {
    "tl_y": 40.85,
    "tl_x": -74.10,
    "br_y": 40.65,
    "br_x": -73.90
}
LOCATION_HOME = [40.75, -74.00, 0.010]
WEATHER_LOCATION = "New York, NY"
BRIGHTNESS = 50
GPIO_SLOWDOWN = 4
MIN_ALTITUDE = 100
TEMPERATURE_UNITS = "imperial"
JOURNEY_CODE_SELECTED = "LGA"
JOURNEY_BLANK_FILLER = " ? "
HAT_PWM_ENABLED = False
HARDWARE_PULSE = False
OPENWEATHER_API_KEY = ""
```

### 4. Create run_emulator.py

```python
import sys
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics

# patch rgbmatrix to use emulator
sys.modules['rgbmatrix'] = type(sys)('rgbmatrix')
sys.modules['rgbmatrix'].RGBMatrix = RGBMatrix
sys.modules['rgbmatrix'].RGBMatrixOptions = RGBMatrixOptions
sys.modules['rgbmatrix'].graphics = graphics

# run the app
import runpy
runpy.run_path('flight-tracker.py', run_name='__main__')
```

### 5. Run the emulator

```bash
python run_emulator.py
```

A window shows the 64x32 LED simulation. Edit scenes in `scenes/`, restart to test changes.

## License

GPL v3.0 - Same as original. See [LICENSE](LICENSE).
