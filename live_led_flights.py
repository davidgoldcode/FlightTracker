# live_led_flights.py
import time
from FlightRadar24 import FlightRadar24API
from led_simulator import set_pixel, clear_panel, draw_panel
import pygame

update_led = set_pixel
clear_leds = clear_panel

PANEL_WIDTH = 64
PANEL_HEIGHT = 32

fr_api = FlightRadar24API()


def map_coords(lat, lon):
    x = int((lon + 180) / 360 * PANEL_WIDTH)
    y = int((90 - lat) / 180 * PANEL_HEIGHT)
    return x, y


try:
    running = True
    while running:
        # Pump pygame events so the window doesn't freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        flights = fr_api.get_flights()
        clear_leds()

        for flight in flights:
            if hasattr(flight, "latitude") and hasattr(flight, "longitude"):
                x, y = map_coords(flight.latitude, flight.longitude)
                color = (255, 0, 0)
                update_led(x, y, color)

        draw_panel()
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting simulator...")

finally:
    clear_leds()
    draw_panel()
    pygame.quit()
