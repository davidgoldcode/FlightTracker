from time import sleep

DELAY_DEFAULT = 0.01

# reserved screen regions that persistent scenes use
# idle animations must clear these areas before drawing
CLOCK_REGION_Y = (0, 10)  # clock draws at y=0-8, we clear y=0-10 for safety


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

        self._register_keyframes()

        super().__init__()

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
