import pygame
import time
import random

# If you have FlightTracker code, import it here
# For now we’ll use dummy flights
# from flighttracker import tracker

PANEL_WIDTH = 64
PANEL_HEIGHT = 32
LED_SIZE = 15
FPS = 10

pygame.init()
screen = pygame.display.set_mode((PANEL_WIDTH * LED_SIZE, PANEL_HEIGHT * LED_SIZE))
pygame.display.set_caption("FlightTracker LED Simulator")
clock = pygame.time.Clock()

# Panel state
panel = [[(0, 0, 0) for _ in range(PANEL_WIDTH)] for _ in range(PANEL_HEIGHT)]


def draw_panel():
    for y in range(PANEL_HEIGHT):
        for x in range(PANEL_WIDTH):
            color = panel[y][x]
            pygame.draw.rect(
                screen, color, (x * LED_SIZE, y * LED_SIZE, LED_SIZE - 1, LED_SIZE - 1)
            )
    pygame.display.flip()


def set_pixel(x, y, color):
    if 0 <= x < PANEL_WIDTH and 0 <= y < PANEL_HEIGHT:
        panel[y][x] = color


def clear_panel():
    for y in range(PANEL_HEIGHT):
        for x in range(PANEL_WIDTH):
            panel[y][x] = (0, 0, 0)


# --- Example function to map lat/lon to panel coordinates ---
def latlon_to_xy(lat, lon):
    # Replace with your real bounding box logic later
    # For now, random positions to simulate flights
    x = int(random.random() * PANEL_WIDTH)
    y = int(random.random() * PANEL_HEIGHT)
    return x, y


# --- Example flight data ---
flights = [
    {
        "icao": "A12345",
        "lat": 40.7,
        "lon": -74.0,
        "altitude": 30000,
        "color": (255, 0, 0),
    },
    {
        "icao": "B67890",
        "lat": 40.71,
        "lon": -74.01,
        "altitude": 28000,
        "color": (0, 255, 0),
    },
    {
        "icao": "C24680",
        "lat": 40.72,
        "lon": -74.02,
        "altitude": 25000,
        "color": (0, 0, 255),
    },
]


def update_panel(flights):
    clear_panel()
    for f in flights:
        x, y = latlon_to_xy(f["lat"], f["lon"])
        set_pixel(x, y, f["color"])
    draw_panel()


# --- Main loop ---
def run_simulator():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Here you could call FlightTracker’s code instead of dummy data
        # flights = tracker.get_current_flights()  # example
        update_panel(flights)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_simulator()
