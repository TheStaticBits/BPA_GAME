import pygame

CAP_FPS = True # True/False to cap FPS
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
JUMP_FORCE = 3.6 # Upward force
GRAVITY = 0.2 # Downward force
MOVEMENT_SPEED = 2

# temporary, 1 is the default, -1 means it inverses.
INVERSE_GRAVITY = 1

# Tiles
# first value indicating the string in the level layout
# second value is the folder name of the tile
TILE_KEYS = {
    "w": "default",
    "c": "crystal",
    "s": "star",
    "d": "dirt",
    "b": "blank"
}

# These tiles are the ones which are not solid
# A background tile is drawn behind these tiles
# Wall tiles will not connect to these tiles
TRANSPARENT_TILES = (
    " ",
    "^", "<", "v", ">"
)

# Other tiles
SPIKE_PATH = "res/misc/spike.png"
SPIKE_ROTATIONS = {
    "^": 0,
    "<": 90,
    "v": 180,
    ">": 270
}
