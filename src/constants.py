import pygame

SAVE_PATH = "saves/save.db" # The save file's path
EVENT_LOG_PATH = "saves/events.log" # The event log's path

CAP_FPS = True # True/False to cap FPS
FPS = 60 # Frame rate of the screen

TILE_SIZE = (16, 16) # Size in pixels of the tiles
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

# Default save (for the database)
DEFAULT_SAVE = {
    "playerX": -1,
    "playerY": -1,
    "playerVelocity": 0,
    "level": 0,
    "room": 0,
}

# Solid Tiles
# first value indicating the string in the level layout
# second value is the folder name of the tile
TILE_KEYS = {
    "w": "default",
    "c": "crystal",
    "s": "star",
    "d": "dirt",
    "b": "blank",
    "e": "darkness",
    "l": "blue"
}

# These tiles are the ones which are not solid
# A background tile is drawn behind these tiles
# Wall tiles will not connect to these tiles
TRANSPARENT_TILES = (
    " ",
    "p",
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

# Gravity beam path
GRAV_BEAM_PATH = "res/misc/grav_beam.png"
GRAV_BEAM_DELAY = 2 # Delay between each frame of the beam
GRAV_BEAM_WIDTH = 8 # Width of the beam