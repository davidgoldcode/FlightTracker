try:
    import RPi.GPIO as GPIO
except ImportError:
    import dummy_gpio as GPIO  # <- alias the module as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
GPIO.cleanup()

print("Dummy GPIO ran without errors!")
