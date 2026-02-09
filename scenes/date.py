from datetime import datetime

from utilities.animator import Animator
from setup import colours, fonts, frames

from rgbmatrix import graphics

# Setup
DATE_COLOUR = colours.PINK_DARKER
DATE_FONT = fonts.small
DATE_POSITION = (1, 31)


class DateScene(object):
    def __init__(self):
        super().__init__()
        self._last_date = None

    # zx_ prefix ensures this runs AFTER all idle animations in alphabetical
    # keyframe order, so _idle_drawn_this_frame is already set correctly
    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def zx_date(self, count):
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_date = None

        elif self._idle_drawn_this_frame:
            # An idle animation (holiday, ambient) is active - don't draw date
            # The idle animation owns the whole screen
            self._last_date = None

        else:
            # If there's no data to display and no idle animation active
            # then draw the date
            now = datetime.now()
            current_date = now.strftime("%a %b %-d")

            # Only draw if date needs updated
            if self._last_date != current_date:
                # Undraw last date if different from current
                if self._last_date is not None:
                    _ = graphics.DrawText(
                        self.canvas,
                        DATE_FONT,
                        DATE_POSITION[0],
                        DATE_POSITION[1],
                        colours.BLACK,
                        self._last_date,
                    )
                self._last_date = current_date

                # Draw date
                _ = graphics.DrawText(
                    self.canvas,
                    DATE_FONT,
                    DATE_POSITION[0],
                    DATE_POSITION[1],
                    DATE_COLOUR,
                    current_date,
                )
