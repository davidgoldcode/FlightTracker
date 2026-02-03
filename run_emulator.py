import sys

# pygame-ce installs as 'pygame' module
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics

# patch rgbmatrix module to use emulator
sys.modules['rgbmatrix'] = type(sys)('rgbmatrix')
sys.modules['rgbmatrix'].RGBMatrix = RGBMatrix
sys.modules['rgbmatrix'].RGBMatrixOptions = RGBMatrixOptions
sys.modules['rgbmatrix'].graphics = graphics

# run the app
import runpy
runpy.run_path('flight-tracker.py', run_name='__main__')
