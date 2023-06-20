import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mech Mayhem")

# Define colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define Mech class
class Mech:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def move(self):
        # Randomly move the mech
        self.x += random.randint(-5, 5)
        self.y += random.randint(-5, 5)

        # Keep the mech within the screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH))
        self.y = max(0, min(self.y, SCREEN_HEIGHT))

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 20)

# Create player mech and computer mech
player_mech = Mech(100, 100, RED)
computer_mech = Mech(400, 300, BLUE)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the mechs
    player_mech.move()
    computer_mech.move()

    # Clear the screen
    screen.fill(BLACK)

    # Draw the mechs
    player_mech.draw()
    computer_mech.draw()

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()