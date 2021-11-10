import pygame

FPS = 60 # Frame rate of the screen

TILE_SIZE = (16, 16)
SCREEN_TILE_SIZE = (24, 14) # Amount of tiles on the screen by X and Y

# These are the separaters in the levels.txt file.
LEVEL_SEPARATOR = "\n------------------------\n"
ROOM_SEPARATOR = "\n||||||||||||||||||||||||\n"

PX_SCALE_FACTOR = 3 # This is the scale factor of everything being rendered to the screen

# These are the keys which will trigger the movement of the player.
LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
UP_KEYS = (pygame.K_UP, pygame.K_w)

# Player constants
JUMP_FORCE = 3.2 # Upward force
GRAVITY = 0.2 # Downward force
MOVEMENT_SPEED = 2

# Tiles
# first value indicating the string in the level layout
# second value is the folder name of the tile
TILE_KEYS = {
    "w": "other_tile_test",
    "c": "crystal"
}