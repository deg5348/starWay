import pygame
import sys

# Initialize Pygame
pygame.init()

# Set the width and height of the screen (width, height)
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Player GIF")

# Load the GIF image
player_gif = pygame.image.load("blackhole.png")

# Get the rectangle of the image for positioning
player_rect = player_gif.get_rect()

# Set the initial position of the player
player_rect.centerx = screen_width // 2
player_rect.centery = screen_height // 2

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Blit the player GIF onto the screen
    screen.blit(player_gif, player_rect)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.delay(10)
