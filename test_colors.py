#!/usr/bin/env python3
"""
Test RGB channels to diagnose color issues.
Shows pure R, G, B squares so you can see which channels work.
"""
import time
import sys

# try emulator first (Mac), fall back to real hardware (Pi)
try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    USE_EMULATOR = True
except ImportError:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    USE_EMULATOR = False

print("\n🎨 Color Channel Test")
if USE_EMULATOR:
    print("   Open http://localhost:8888 in your browser")
else:
    print("   Running on LED hardware")
print()

# setup matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.hardware_mapping = "adafruit-hat"
options.brightness = 50
options.gpio_slowdown = 4
options.disable_hardware_pulsing = True

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

def fill_rect(x, y, w, h, r, g, b):
    for px in range(x, x + w):
        for py in range(y, y + h):
            if 0 <= px < 64 and 0 <= py < 32:
                canvas.SetPixel(px, py, r, g, b)

print("Showing color test pattern:")
print("  Left:   Pure RED (255, 0, 0)")
print("  Middle: Pure GREEN (0, 255, 0)")
print("  Right:  Pure BLUE (0, 0, 255)")
print()
print("What you SHOULD see: Red | Green | Blue")
print("Press CTRL-C to exit\n")

try:
    while True:
        canvas.Clear()

        # pure red - left third
        fill_rect(0, 0, 21, 32, 255, 0, 0)

        # pure green - middle third
        fill_rect(22, 0, 21, 32, 0, 255, 0)

        # pure blue - right third
        fill_rect(44, 0, 20, 32, 0, 0, 255)

        # labels at bottom
        graphics.DrawText(canvas, graphics.Font(), 5, 28, graphics.Color(255,255,255), "R")
        graphics.DrawText(canvas, graphics.Font(), 28, 28, graphics.Color(255,255,255), "G")
        graphics.DrawText(canvas, graphics.Font(), 50, 28, graphics.Color(255,255,255), "B")

        matrix.SwapOnVSync(canvas)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped")
    canvas.Clear()
    matrix.SwapOnVSync(canvas)
