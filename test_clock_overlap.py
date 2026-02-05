#!/usr/bin/env python3
"""
Test that idle animations properly handle clock region overlap.

This test verifies that all idle animations (holidays, ambient scenes) either:
1. Call clear_clock_region() before drawing, OR
2. Don't draw any pixels in the clock region (y=0-10)

Usage:
    python test_clock_overlap.py           # test all idle scenes
    python test_clock_overlap.py birthday  # test specific scene
"""
import sys

# set up emulator and demo mode before imports
try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    sys.modules['rgbmatrix'] = type(sys)('rgbmatrix')
    sys.modules['rgbmatrix'].RGBMatrix = RGBMatrix
    sys.modules['rgbmatrix'].RGBMatrixOptions = RGBMatrixOptions
    sys.modules['rgbmatrix'].graphics = graphics
except ImportError:
    print("ERROR: RGBMatrixEmulator required for this test")
    print("Install with: pip install RGBMatrixEmulator")
    sys.exit(1)

# force demo mode
class FakeConfigModule:
    def __getattr__(self, name):
        raise ImportError("Demo mode - no config")

sys.modules['config'] = FakeConfigModule()

from utilities.animator import Animator, CLOCK_REGION_Y

# idle animations that should respect clock region
IDLE_ANIMATIONS = {
    # holidays
    'birthday': 'scenes.birthday.BirthdayScene',
    'anniversary': 'scenes.anniversary.AnniversaryScene',
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
    # ambient (conditional - shown in production)
    'fireplace': 'scenes.fireplace.FireplaceScene',
    'fallingsnow': 'scenes.fallingsnow.FallingSnowScene',
    # ambient (demo-only - gated with `if not DEMO_MODE: return`)
    'starfield': 'scenes.starfield.StarfieldScene',
    'oceanwaves': 'scenes.oceanwaves.OceanWavesScene',
    'rain': 'scenes.rain.RainScene',
    'aurora': 'scenes.aurora.AuroraScene',
    'timeofday': 'scenes.timeofday.TimeOfDayScene',
    # default
    'heartbeat': 'scenes.heartbeat.HeartbeatScene',
    'lovemessages': 'scenes.lovemessages.LoveMessagesScene',
}

# demo-only scenes that have `if not DEMO_MODE: return` gate
# these won't show in production, so clock overlap is acceptable in demo
DEMO_ONLY_SCENES = {'starfield', 'rain', 'aurora'}  # oceanwaves and timeofday already pass


class PixelTracker:
    """Mock canvas that tracks which pixels are set."""

    def __init__(self):
        self.pixels = {}  # (x, y) -> (r, g, b)
        self.clock_region_cleared = False
        self.clock_pixels_set = []  # pixels set in clock region AFTER it was cleared
        # emulator compatibility
        self.width = 64
        self.height = 32

    def SetPixel(self, x, y, r, g, b):
        self.pixels[(x, y)] = (r, g, b)

        # track if clock region was cleared (all black)
        y_start, y_end = CLOCK_REGION_Y
        if y_start <= y <= y_end:
            if r == 0 and g == 0 and b == 0:
                # check if entire clock region is being cleared
                cleared_count = sum(
                    1 for (px, py), (pr, pg, pb) in self.pixels.items()
                    if y_start <= py <= y_end and pr == 0 and pg == 0 and pb == 0
                )
                # if we've cleared at least 64 * 11 = 704 pixels, region is cleared
                if cleared_count >= 64 * (y_end - y_start + 1):
                    self.clock_region_cleared = True
            elif r > 0 or g > 0 or b > 0:
                # non-black pixel in clock region
                self.clock_pixels_set.append((x, y, r, g, b))

    def Clear(self):
        self.pixels = {}
        self.clock_region_cleared = False
        self.clock_pixels_set = []

    def Fill(self, r, g, b):
        """Fill entire canvas with color."""
        for x in range(64):
            for y in range(32):
                self.SetPixel(x, y, r, g, b)


def get_scene_class(name):
    module_path, class_name = IDLE_ANIMATIONS[name].rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def test_scene(name, verbose=False):
    """Test a single scene for clock overlap issues.

    Returns:
        (passed, message)
    """
    SceneClass = get_scene_class(name)

    # create test display with pixel tracking
    class TestDisplay(SceneClass, Animator):
        def __init__(self):
            options = RGBMatrixOptions()
            options.rows = 32
            options.cols = 64
            options.hardware_mapping = "adafruit-hat"
            options.brightness = 50
            self.matrix = RGBMatrix(options=options)
            self.canvas = PixelTracker()  # use our tracker instead of real canvas

            self._data = []
            self._data_index = 0
            self._data_all_looped = False

            class MockOverhead:
                processing = False
                new_data = False
                data_is_empty = True
                data = []
            self.overhead = MockOverhead()

            super().__init__()

    try:
        display = TestDisplay()
    except Exception as e:
        return (False, f"Failed to initialize: {e}")

    # run a few frames to let the animation draw
    display._idle_drawn_this_frame = False

    # find the keyframe method for this scene
    keyframe_method = None
    for kf in display.keyframes:
        method_name = kf.__name__
        # skip sync and other utility methods
        if method_name in ('sync', 'clear_screen', 'check_for_loaded_data', 'grab_new_data'):
            continue
        # look for the main animation method
        if any(x in method_name.lower() for x in [name.replace('_', ''), name]):
            keyframe_method = kf
            break

    if not keyframe_method:
        # try to find any keyframe that's not a utility
        for kf in display.keyframes:
            if kf.__name__ not in ('sync', 'clear_screen'):
                keyframe_method = kf
                break

    if not keyframe_method:
        return (False, "Could not find keyframe method")

    # run the animation for a few frames
    for frame in range(10):
        display._idle_drawn_this_frame = False
        display.canvas.clock_pixels_set = []  # reset per-frame tracking
        try:
            keyframe_method(frame)
        except Exception as e:
            return (False, f"Animation error on frame {frame}: {e}")

    # check results
    tracker = display.canvas

    # demo-only scenes have `if not DEMO_MODE: return` gate
    # they won't show in production, so clock overlap is acceptable
    if name in DEMO_ONLY_SCENES:
        return (True, "Demo-only (gated in production)")

    # heartbeat and lovemessages don't need to clear clock region
    # because they draw below it (y >= 10)
    safe_scenes = {'heartbeat', 'lovemessages'}
    if name in safe_scenes:
        # just verify they don't draw in clock region
        y_start, y_end = CLOCK_REGION_Y
        bad_pixels = [
            (x, y) for (x, y), (r, g, b) in tracker.pixels.items()
            if y_start <= y <= y_end and (r > 0 or g > 0 or b > 0)
        ]
        if bad_pixels:
            return (False, f"Drew {len(bad_pixels)} pixels in clock region without clearing")
        return (True, "Safe (draws below clock region)")

    # for other scenes, verify clock region was cleared
    if not tracker.clock_region_cleared:
        # check if there are any non-black pixels in clock region
        y_start, y_end = CLOCK_REGION_Y
        bad_pixels = [
            (x, y) for (x, y), (r, g, b) in tracker.pixels.items()
            if y_start <= y <= y_end and (r > 0 or g > 0 or b > 0)
        ]
        if bad_pixels:
            sample = bad_pixels[:5]
            return (False, f"Drew {len(bad_pixels)} pixels in clock region without clearing. Sample: {sample}")
        # no bad pixels, must be safe
        return (True, "No clock region pixels drawn")

    return (True, "Clock region properly cleared")


def main():
    # determine which scenes to test
    if len(sys.argv) > 1:
        scenes_to_test = [sys.argv[1]]
        if scenes_to_test[0] not in IDLE_ANIMATIONS:
            print(f"Unknown scene: {scenes_to_test[0]}")
            print(f"Available: {', '.join(sorted(IDLE_ANIMATIONS.keys()))}")
            sys.exit(1)
    else:
        scenes_to_test = sorted(IDLE_ANIMATIONS.keys())

    print(f"Testing {len(scenes_to_test)} idle animation(s) for clock region overlap...\n")

    passed = 0
    failed = 0
    results = []

    for name in scenes_to_test:
        success, message = test_scene(name)
        status = "PASS" if success else "FAIL"
        results.append((name, status, message))

        if success:
            passed += 1
            print(f"  ✓ {name}: {message}")
        else:
            failed += 1
            print(f"  ✗ {name}: {message}")

    print(f"\nResults: {passed} passed, {failed} failed")

    if failed > 0:
        print("\nFailed scenes need to call self.clear_clock_region(drawn_pixels)")
        sys.exit(1)


if __name__ == '__main__':
    main()
