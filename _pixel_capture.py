"""Monkey-patch for RGBMatrixEmulator to capture pixel data to a shared file.

Import this AFTER setting up the emulator but BEFORE creating the matrix.
It patches the Canvas class to write raw RGB bytes on every SwapOnVSync.
"""
import os
import numpy as np
from pathlib import Path

BRIDGE_PATH = Path(__file__).parent / "_pixel_bridge.bin"


def patch_emulator():
    """Patch RGBMatrixEmulator to dump pixels to a binary file each frame."""
    try:
        from RGBMatrixEmulator.emulation.canvas import Canvas

        original_draw = Canvas.draw_to_screen

        def patched_draw(self):
            # write raw pixel bytes (32*64*3 = 6144 bytes)
            try:
                pixels = self._Canvas__pixels  # access name-mangled private attr
                if pixels is not None:
                    raw = np.ascontiguousarray(pixels, dtype=np.uint8).tobytes()
                    # atomic write via temp file
                    tmp = BRIDGE_PATH.with_suffix('.tmp')
                    tmp.write_bytes(raw)
                    tmp.rename(BRIDGE_PATH)
            except Exception:
                pass

            # call original
            return original_draw(self)

        Canvas.draw_to_screen = patched_draw

    except ImportError:
        pass  # not using emulator, skip


def cleanup():
    """Remove the bridge file."""
    try:
        BRIDGE_PATH.unlink(missing_ok=True)
        BRIDGE_PATH.with_suffix('.tmp').unlink(missing_ok=True)
    except Exception:
        pass
