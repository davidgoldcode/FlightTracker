#!/usr/bin/env python3
"""
Test individual animations in isolation with scenario support.

Usage:
    python test_animation.py <animation>
    python test_animation.py <animation> --scenario=<scenario>

Scenarios (for birthday/anniversary):
    --scenario=day-of       Show the "day of" celebration
    --scenario=countdown:N  Show N days countdown (e.g., countdown:3)

Examples:
    python test_animation.py birthday
    python test_animation.py birthday --scenario=day-of
    python test_animation.py birthday --scenario=countdown:1
    python test_animation.py anniversary --scenario=countdown:5
"""
import sys

# parse scenario arg before other imports
scenario = None
for arg in sys.argv[1:]:
    if arg.startswith('--scenario='):
        scenario = arg.split('=', 1)[1]
        sys.argv.remove(arg)
        break

# try emulator first (Mac), fall back to real hardware (Pi)
try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    sys.modules['rgbmatrix'] = type(sys)('rgbmatrix')
    sys.modules['rgbmatrix'].RGBMatrix = RGBMatrix
    sys.modules['rgbmatrix'].RGBMatrixOptions = RGBMatrixOptions
    sys.modules['rgbmatrix'].graphics = graphics
    USE_EMULATOR = True
except ImportError:
    # on Pi, use real hardware
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    USE_EMULATOR = False

# force demo mode by removing config module so scenes fall back to demo mode
# this ensures all animations render even if config has holidays disabled
if 'config' in sys.modules:
    del sys.modules['config']

# create a fake config that raises ImportError to trigger demo mode
class FakeConfigModule:
    def __getattr__(self, name):
        raise ImportError("Demo mode - no config")

sys.modules['config'] = FakeConfigModule()

print("\n✨ Animation Tester (Demo Mode)")
if USE_EMULATOR:
    print("   Open http://localhost:8888 in your browser")
else:
    print("   Running on LED hardware")
if scenario:
    print(f"   Scenario: {scenario}")
print()

from utilities.animator import Animator
from setup import frames

# available animations to test
ANIMATIONS = {
    'heartbeat': 'scenes.heartbeat.HeartbeatScene',
    'clock': 'scenes.clock.ClockScene',
    'weather': 'scenes.weather.WeatherScene',
    'date': 'scenes.date.DateScene',
    'day': 'scenes.day.DayScene',
    'lovemessages': 'scenes.lovemessages.LoveMessagesScene',
    'starfield': 'scenes.starfield.StarfieldScene',
    'oceanwaves': 'scenes.oceanwaves.OceanWavesScene',
    'fallingsnow': 'scenes.fallingsnow.FallingSnowScene',
    'aurora': 'scenes.aurora.AuroraScene',
    'fireplace': 'scenes.fireplace.FireplaceScene',
    'rain': 'scenes.rain.RainScene',
    'birthday': 'scenes.birthday.BirthdayScene',
    'anniversary': 'scenes.anniversary.AnniversaryScene',
    'timeofday': 'scenes.timeofday.TimeOfDayScene',
    'valentines': 'scenes.valentines.ValentinesScene',
    'halloween': 'scenes.halloween.HalloweenScene',
    'chanukah': 'scenes.chanukah.ChanukahScene',
    'newyear': 'scenes.newyear.NewYearScene',
    'christmas': 'scenes.christmas.ChristmasScene',
    'stpatricks': 'scenes.stpatricks.StPatricksScene',
    'easter': 'scenes.easter.EasterScene',
    'independence': 'scenes.independence.IndependenceScene',
    'thanksgiving': 'scenes.thanksgiving.ThanksgivingScene',
    'chinesenewyear': 'scenes.chinesenewyear.ChineseNewYearScene',
    'planeintro': 'scenes.planeintro.PlaneIntroScene',
}

# animations that support scenarios
SCENARIO_ANIMATIONS = {'birthday', 'anniversary'}


def parse_scenario(scenario_str):
    """Parse scenario string into (type, value).

    Returns:
        ('day-of', None) for day-of celebrations
        ('countdown', N) for countdown scenarios
        (None, None) for default/demo mode
    """
    if not scenario_str:
        return (None, None)

    if scenario_str == 'day-of':
        return ('day-of', 0)

    if scenario_str.startswith('countdown:'):
        try:
            days = int(scenario_str.split(':')[1])
            return ('countdown', days)
        except (ValueError, IndexError):
            print(f"Invalid countdown format: {scenario_str}")
            print("Use: --scenario=countdown:N (e.g., countdown:3)")
            sys.exit(1)

    print(f"Unknown scenario: {scenario_str}")
    print("Available: day-of, countdown:N")
    sys.exit(1)


def get_scene_class(name):
    if name not in ANIMATIONS:
        print(f"Unknown animation: {name}")
        print(f"Available: {', '.join(sorted(ANIMATIONS.keys()))}")
        sys.exit(1)

    module_path, class_name = ANIMATIONS[name].rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_animation.py <animation> [--scenario=<scenario>]")
        print(f"\nAvailable animations: {', '.join(sorted(ANIMATIONS.keys()))}")
        print("\nScenarios (for birthday/anniversary):")
        print("  --scenario=day-of       Show the celebration")
        print("  --scenario=countdown:N  Show N days countdown")
        sys.exit(1)

    animation_name = sys.argv[1]
    SceneClass = get_scene_class(animation_name)

    # parse scenario
    scenario_type, scenario_value = parse_scenario(scenario)

    # warn if scenario used with non-supporting animation
    if scenario and animation_name not in SCENARIO_ANIMATIONS:
        print(f"Warning: {animation_name} doesn't support scenarios, ignoring --scenario")

    # create minimal display with just this animation
    class TestDisplay(SceneClass, Animator):
        def __init__(self):
            options = RGBMatrixOptions()
            options.rows = 32
            options.cols = 64
            options.hardware_mapping = "adafruit-hat"
            options.brightness = 50
            options.gpio_slowdown = 4  # required for Pi hardware
            options.disable_hardware_pulsing = True
            self.matrix = RGBMatrix(options=options)
            self.canvas = self.matrix.CreateFrameCanvas()
            self.canvas.Clear()

            # mock data (empty = no flights, triggers idle animations)
            self._data = []
            self._data_index = 0
            self._data_all_looped = False

            # mock overhead for scenes that check it
            class MockOverhead:
                processing = False
                new_data = False
                data_is_empty = True
                data = []
            self.overhead = MockOverhead()

            super().__init__()
            self.delay = frames.PERIOD

            # apply scenario after init
            if animation_name in SCENARIO_ANIMATIONS and scenario_type:
                self._apply_scenario(scenario_type, scenario_value)

        def _apply_scenario(self, stype, svalue):
            """Apply scenario to the display."""
            if stype == 'day-of':
                # set scenario to day-of (0 days)
                if hasattr(self, '_scenario_days'):
                    self._scenario_days = 0
            elif stype == 'countdown':
                # set scenario to countdown
                if hasattr(self, '_scenario_days'):
                    self._scenario_days = svalue

        @Animator.KeyFrame.add(1)
        def sync(self, count):
            self.matrix.SwapOnVSync(self.canvas)

        def run(self):
            print(f"Testing: {animation_name}")
            if scenario:
                print(f"Scenario: {scenario}")
            print("Press CTRL-C to stop\n")
            try:
                self.play()
            except KeyboardInterrupt:
                print("\nStopped")
                sys.exit(0)

    display = TestDisplay()
    display.run()

if __name__ == '__main__':
    main()
