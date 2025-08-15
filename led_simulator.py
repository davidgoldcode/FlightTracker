import pygame
import time

# Panel dimensions (64x32 LEDs)
PANEL_WIDTH = 64
PANEL_HEIGHT = 32
LED_SIZE = 15  # Size of each “LED” in pixels
FPS = 10  # Frames per second

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((PANEL_WIDTH * LED_SIZE, PANEL_HEIGHT * LED_SIZE))
pygame.display.set_caption("FlightTracker LED Simulator")
clock = pygame.time.Clock()

# Example: create a blank panel
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


# Demo: animate some fake flights
def demo_flights():
    clear_panel()
    positions = [(5, 5), (10, 20), (30, 15), (50, 28)]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    dx = [1, -1, 1, -1]
    dy = [1, 1, -1, -1]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clear_panel()
        for i, (x, y) in enumerate(positions):
            set_pixel(x, y, colors[i])
            positions[i] = (x + dx[i], y + dy[i])
            # bounce off edges
            if positions[i][0] <= 0 or positions[i][0] >= PANEL_WIDTH - 1:
                dx[i] = -dx[i]
            if positions[i][1] <= 0 or positions[i][1] >= PANEL_HEIGHT - 1:
                dy[i] = -dy[i]

        draw_panel()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    demo_flights()
