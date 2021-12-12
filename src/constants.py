import pygame

import src.utility as utility

SAVE_PATH = "saves/save.db"
EVENT_LOG_PATH = "saves/events.log"

FONT_PATH = "res/font/monogram.ttf"
FONT_SIZE = 15

LEVELS_PATH = "data/levels.txt"

CUTSCENE_DATA_PATH = "data/cutscenes.json"

MAIN_MENU_LEVEL_PATH = "data/menu_level.txt"
LOGO_PATH = "res/misc/logo.png"

EMAIL_PWD_PATH = "data/emailpassword.txt"

MUSIC_FOLDER = "res/sound"

SCREEN_SHADOW_PATH = "res/misc/shadow.png"

CRYSTAL_CHECK_PATH = "res/misc/crystal_check.png"
CRYSTAL_X_PATH = "res/misc/crystal_x.png"

BUTTON_HIGHLIGHT_SPEED = 10 # The higher this goes, the slower buttons fills up when hovering a mouse over it.

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

CAP_FPS = True # True/False to cap FPS
FPS = 60 # Frame rate of the screen

TILE_SIZE = (16, 16) # Size in pixels of the tiles
SCREEN_TILE_SIZE = (24, 14) # Amount of tiles on the screen by X and Y
SCREEN_SIZE = (
    SCREEN_TILE_SIZE[0] * TILE_SIZE[0], 
    SCREEN_TILE_SIZE[1] * TILE_SIZE[1]
) # Size of the screen in pixels, not including scale factor

PX_SCALE_FACTOR = 3 # This is the scale factor of everything being rendered to the screen

# These are the separaters in the levels.txt file.
LEVEL_SEPARATOR = "\n------------------------\n"
ROOM_SEPARATOR = "\n||||||||||||||||||||||||\n"

# The assignment of leveldata
ASSIGNMENT_SEPARATOR = " = "

# These are the keys which will trigger the movement of the player.
LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
UP_KEYS = (pygame.K_UP, pygame.K_w)

# Player constants
JUMP_FORCE = 3.6 # Upward force
GRAVITY = 0.2 # Downward force
MAX_SPEED = 2 # Maximum left/right speed
SPEED_UP_SPEED = 0.3 # How quickly the player accelerates/decelerates

CORLEN_FOLLOW_DISTANCE = 10 # How far behind Corlen is from the player
ELLIPSE_FOLLOW_DISTANCE = 22 # How far behind Ellipse is from the player
MAX_FOLLOW_DISTANCE = 22 # Player positions stored

# Default save (for the database)
DEFAULT_SAVE = {
    "levels": "00000000000000000000000000",
    "level": 0,
    "crystals": "00000000000000000"
}

# Solid Tiles
# first value indicating the string in the level layout
# second value is the folder name of the tile
TILE_KEYS = {
    "w": "default",
    "o": "crystal",
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
    " ", # Air tile
    "p", # Player start tile
    "^", "<", "v", ">", # Spikes
    "j", # Jump orb
    "g",
    "c",
    "m"
)

# Tiles that have special actions
# They are handled by the individual entities
SPECIAL_TILES = (
    "^", "<", "v", ">", # Spikes
    "j", # Jump orb
    "g", # Gravity orb
    "c", # Crystal
    "m"  # Gravity button
)

# These tiles have animations
TILES_WITH_ANIMATIONS = utility.load_json("res/tiles/animated/anim_dat.json")

PLAYER_ANIMATIONS = utility.load_json("res/characters/player/animations.json")
PLAYER_WIDTH = 8

ELLIPSE_ANIMATIONS = utility.load_json("res/characters/ellipse/animations.json")

CORLEN_ANIMATIONS = utility.load_json("res/characters/corlen/animations.json")

# The Belloq is the first boss
# This holds the animations for the Belloq, their paths, frames, and delays
BELLOQ_ANIMATIONS = utility.load_json("res/characters/belloq/animations.json")
BELLOQ_SPEED = 0.5 # Pixels moved per frame
BELLOQ_COOLDOWN = 80 # Frames between lazers
BELLOQ_LAZER_OFFSET = (33, 17) # Position of the eye in relation to the top left of the sprite
# Where the lazer fires from
BELLOQ_LAZER_ACCURACY = 0.2 # A random number chosen between the negative of this number and the positive of this number will be added onto the lazer's direction
# Can only be up to the hundreths in decimal places
# Is in randians
# If it's zero, it will have perfect accuracy

# Belloq boss constants
LAZER_SPEED = 2
LAZER_LENGTH = 20
LAZER_COLOR = (255, 255, 0)

# Big Bite Boss constants
BIG_BITE_ANIM_PATH = "res/characters/big_bite/anim.png"
BIG_BITE_ATTACK_FRAME = 3 # The frame number in the animation in which collisions are checked between the player and the boss
BIG_BITE_TOTAL_FRAMES = 5
BIG_BITE_DELAY = 15 # The delay between frames in the animation, in game frames (60 frames per second)
BIG_BITE_ATTACK_DELAY = (5, 40) # The delay between each attack in frames. It is randomly chosen between these two numbers

# Other tiles
SPIKE_PATH = "res/misc/spike.png"
SPIKE_ROTATIONS = {
    "^": 0,
    "<": 90,
    "v": 180,
    ">": 270
}

# Gravity beam data
GRAV_BEAM_PATH = "res/misc/grav_beam.png"
GRAV_BEAM_DELAY = 2 # Delay between each frame of the beam
GRAV_BEAM_WIDTH = 8 # Width of the beam

GRAV_BEAM_TILE_Y_POS = SCREEN_TILE_SIZE[1] / 2