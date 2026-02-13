from utilities.animator import Animator
from utilities.datenow import get_now
from setup import colours, fonts, frames

from rgbmatrix import graphics

# Setup
CLOCK_FONT = fonts.regular
CLOCK_POSITION = (1, 8)
CLOCK_COLOUR = colours.BLUE_DARK


class ClockScene(object):
    def __init__(self):
        super().__init__()
        self._last_time = None

    # zx_ prefix ensures this runs AFTER all idle animations in alphabetical
    # keyframe order, so _idle_drawn_this_frame is already set correctly
    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def zx_clock(self, count):
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_time = None

        elif self._idle_drawn_this_frame:
            # An idle animation (holiday, ambient) is active - don't draw clock
            # The idle animation owns the whole screen
            if self._last_time is not None:
                _ = graphics.DrawText(
                    self.canvas,
                    CLOCK_FONT,
                    CLOCK_POSITION[0],
                    CLOCK_POSITION[1],
                    colours.BLACK,
                    self._last_time,
                )
                self._last_time = None

        else:
            # If there's no data to display and no idle animation active
            # then draw a clock
            now = get_now()
            current_time = now.strftime("%I:%M%p")

            # Only draw if time needs updated
            if self._last_time != current_time:
                # Undraw last time if different from current
                if self._last_time is not None:
                    _ = graphics.DrawText(
                        self.canvas,
                        CLOCK_FONT,
                        CLOCK_POSITION[0],
                        CLOCK_POSITION[1],
                        colours.BLACK,
                        self._last_time,
                    )
                self._last_time = current_time

                # Draw Time
                _ = graphics.DrawText(
                    self.canvas,
                    CLOCK_FONT,
                    CLOCK_POSITION[0],
                    CLOCK_POSITION[1],
                    CLOCK_COLOUR,
                    current_time,
                )
