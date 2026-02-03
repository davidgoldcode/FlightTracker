# Flight Tracker LED

Personal fork of [ColinWaddell/FlightTracker](https://github.com/ColinWaddell/FlightTracker) with custom animations and configuration for a gift build.

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

See original repo for full instructions. Key flags for this hardware:

```bash
--led-gpio-mapping=adafruit-hat
--led-no-hardware-pulse
--led-slowdown-gpio=4
```

## Custom Features

- 12-hour time format (AM/PM)
- Weather API integration
- Custom animations (WIP)

## Config

```python
LOCATION_HOME = [40.718, -73.964, 0.010]  # Brooklyn, NY
WEATHER_LOCATION = "Brooklyn, NY"
GPIO_SLOWDOWN = 4
HARDWARE_PULSE = False
```

## License

GPL v3.0 - Same as original. See [LICENSE](LICENSE).
