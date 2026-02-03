#!/usr/bin/env python3
"""
Test individual animations in isolation.

Usage:
    python test_animation.py heartbeat
    python test_animation.py clock
    python test_animation.py weather
"""
import sys

# patch rgbmatrix to use emulator
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics

sys.modules['rgbmatrix'] = type(sys)('rgbmatrix')
sys.modules['rgbmatrix'].RGBMatrix = RGBMatrix
sys.modules['rgbmatrix'].RGBMatrixOptions = RGBMatrixOptions
sys.modules['rgbmatrix'].graphics = graphics

print("\n✨ Animation Tester")
print("   Open http://localhost:8888 in your browser\n")

from utilities.animator import Animator
from setup import frames

# available animations to test
ANIMATIONS = {
    'heartbeat': 'scenes.heartbeat.HeartbeatScene',
    'clock': 'scenes.clock.ClockScene',
    'weather': 'scenes.weather.WeatherScene',
    'date': 'scenes.date.DateScene',
    'day': 'scenes.day.DayScene',
}

def get_scene_class(name):
    if name not in ANIMATIONS:
        print(f"Unknown animation: {name}")
        print(f"Available: {', '.join(ANIMATIONS.keys())}")
        sys.exit(1)

    module_path, class_name = ANIMATIONS[name].rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_animation.py <animation>")
        print(f"Available: {', '.join(ANIMATIONS.keys())}")
        sys.exit(1)

    animation_name = sys.argv[1]
    SceneClass = get_scene_class(animation_name)

    # create minimal display with just this animation
    class TestDisplay(SceneClass, Animator):
        def __init__(self):
            options = RGBMatrixOptions()
            options.rows = 32
            options.cols = 64
            options.hardware_mapping = "adafruit-hat"
            options.brightness = 50
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

        @Animator.KeyFrame.add(1)
        def sync(self, count):
            self.matrix.SwapOnVSync(self.canvas)

        def run(self):
            print(f"Testing: {animation_name}")
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
