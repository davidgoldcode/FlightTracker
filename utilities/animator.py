import time
from time import sleep

DELAY_DEFAULT = 0.01
IDLE_CYCLE_SECONDS = 10  # rotate between special occasion scenes
QUIET_AMBIENT_CYCLE_SECONDS = 300  # rotate quiet-hours ambient scenes every 5 minutes

# reserved screen regions that persistent scenes use
# idle animations must clear these areas before drawing
CLOCK_REGION_Y = (0, 10)  # clock draws at y=0-8, we clear y=0-10 for safety
DATE_REGION_Y = (25, 31)  # date draws at y=31, font extends up ~6px


class Animator(object):
    class KeyFrame(object):
        @staticmethod
        def add(divisor, offset=0):
            def wrapper(func):
                func.properties = {"divisor": divisor, "offset": offset, "count": 0}
                return func

            return wrapper

    def __init__(self):
        self.keyframes = []
        self.frame = 0
        self._delay = DELAY_DEFAULT
        self._reset_scene = True
        # mutual exclusion: only one idle animation draws per frame
        self._idle_drawn_this_frame = False

        # special occasion cycling (birthdays + holidays rotate)
        self._special_candidates_prev = []
        self._special_candidates_curr = []
        self._special_winner = None

        # quiet-hours ambient cycling (fireplace, starfield, etc.)
        # uses a persistent set since scenes run at different frame rates
        self._quiet_ambient_registered = set()
        self._quiet_ambient_winner = None

        self._register_keyframes()

        super().__init__()

    def _resolve_special_occasion_cycle(self):
        """Pick which special occasion scene draws this frame.

        Uses previous frame's candidates since we can't know all
        candidates until after they've all registered.
        """
        self._special_candidates_prev = self._special_candidates_curr
        self._special_candidates_curr = []
        if self._special_candidates_prev:
            slot = int(time.time() // IDLE_CYCLE_SECONDS)
            idx = slot % len(self._special_candidates_prev)
            self._special_winner = self._special_candidates_prev[idx]
        else:
            self._special_winner = None

    def _register_special_occasion(self, scene_name):
        """Register as a special occasion candidate and check if it's our turn.

        Returns True if this scene should draw, False otherwise.
        """
        self._special_candidates_curr.append(scene_name)
        if self._special_winner != scene_name:
            return False
        if self._idle_drawn_this_frame:
            return False
        self._idle_drawn_this_frame = True
        return True

    def _resolve_quiet_ambient_cycle(self):
        """Pick which quiet-hours ambient scene draws this frame.

        Uses a persistent set of registered scenes (not per-frame candidates)
        because quiet-ambient scenes run at different frame rates.
        """
        if self._quiet_ambient_registered:
            candidates = sorted(self._quiet_ambient_registered)
            slot = int(time.time() // QUIET_AMBIENT_CYCLE_SECONDS)
            idx = slot % len(candidates)
            self._quiet_ambient_winner = candidates[idx]
        else:
            self._quiet_ambient_winner = None

    def _register_quiet_ambient(self, scene_name):
        """Register as a quiet-hours ambient candidate and check if it's our turn.

        Returns True if this scene should draw, False otherwise.
        """
        self._quiet_ambient_registered.add(scene_name)
        if self._quiet_ambient_winner != scene_name:
            return False
        if self._idle_drawn_this_frame:
            return False
        self._idle_drawn_this_frame = True
        return True

    def clear_clock_region(self, drawn_pixels=None):
        """Clear the clock region (y=0-10) to prevent overlap with idle animations.

        Args:
            drawn_pixels: optional list to append cleared pixel coords to

        Returns:
            list of (x, y) tuples that were cleared
        """
        cleared = []
        y_start, y_end = CLOCK_REGION_Y
        for x in range(64):
            for y in range(y_start, y_end + 1):
                self.canvas.SetPixel(x, y, 0, 0, 0)
                cleared.append((x, y))
        if drawn_pixels is not None:
            drawn_pixels.extend(cleared)
        return cleared

    def clear_date_region(self, drawn_pixels=None):
        """Clear the date region (y=25-31) to prevent overlap with idle animations."""
        cleared = []
        y_start, y_end = DATE_REGION_Y
        for x in range(64):
            for y in range(y_start, y_end + 1):
                self.canvas.SetPixel(x, y, 0, 0, 0)
                cleared.append((x, y))
        if drawn_pixels is not None:
            drawn_pixels.extend(cleared)
        return cleared

    def _register_keyframes(self):
        # Some introspection to setup keyframes
        for methodname in dir(self):
            method = getattr(self, methodname)
            if hasattr(method, "properties"):
                self.keyframes.append(method)

    def reset_scene(self):
        for keyframe in self.keyframes:
            if keyframe.properties["divisor"] == 0:
                keyframe()

    def play(self):
        while True:
            # reset idle animation flag each frame
            self._idle_drawn_this_frame = False
            self._resolve_special_occasion_cycle()
            self._resolve_quiet_ambient_cycle()

            for keyframe in self.keyframes:
                # If divisor == 0 then only run once on first loop
                if self.frame == 0:
                    if keyframe.properties["divisor"] == 0:
                        keyframe()

                # Otherwise perform normal operation
                if (
                    self.frame > 0
                    and keyframe.properties["divisor"]
                    and not (
                        (self.frame - keyframe.properties["offset"])
                        % keyframe.properties["divisor"]
                    )
                ):
                    if keyframe(keyframe.properties["count"]):
                        keyframe.properties["count"] = 0
                    else:
                        keyframe.properties["count"] += 1

            self._reset_scene = False
            self.frame += 1
            sleep(self._delay)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value


if __name__ == "__main__":

    class Test(Animator):
        @Animator.KeyFrame.add(5, 1)
        def method1(self, frame):
            print(f"method1 {frame}")

        @Animator.KeyFrame.add(1, 1)
        def method2(self, frame):
            print(f"method2 {frame}")

    myclass = Test(1)
    myclass.run()

    while 1:
        sleep(5)
