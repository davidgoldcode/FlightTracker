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

## Configuration

Copy `config.example.py` to `config.py` and customize:

```bash
cp config.example.py config.py
nano config.py
```

See [config.example.py](config.example.py) for all options including:

- **Location** - coordinates, weather location, nearby airport
- **Display** - brightness, temperature units
- **Special dates** - birthdays, anniversary
- **Holidays** - Valentine's, Halloween, Chanukah, New Year's, etc.
- **Quiet hours** - dim/ambient mode schedule

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

```bash
cp config.example.py config.py
```

### 4. Run the emulator

```bash
python run_emulator.py
# Open http://localhost:8888 in your browser
```

### 5. Test individual animations

```bash
python test_animation.py heartbeat
python test_animation.py clock
python test_animation.py weather
```

Edit scenes in `scenes/`, restart to test changes.

## License

GPL v3.0 - Same as original. See [LICENSE](LICENSE).
