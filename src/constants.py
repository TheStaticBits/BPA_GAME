import pygame

SAVE_PATH = "saves/save.db"
EVENT_LOG_PATH = "saves/events.log"

FONT_PATH = "res/font/monogram.ttf"
FONT_SIZE = 15

LEVELS_PATH = "data/levels.txt"

CUTSCENE_DATA_PATH = "data/cutscenes.json"
CUTSCENE_LEVELS_PATH = "data/cutscene_levels.txt"

MUSIC_FOLDER = "res/sound"

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
    "playerX": -1,
    "playerY": -1,
    "playerYVelocity": 0,
    "playerXVelocity": 0,
    "globalGravity": 1,
    "level": 0,
    "room": 0,
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
    "c"
)

# Tiles that have special actions
# They are handled by the individual entities
SPECIAL_TILES = (
    "^", "<", "v", ">", # Spikes
    "j", # Jump orb
    "g", # Gravity orb
    "c"
)

# These tiles have animations
TILES_WITH_ANIMATIONS = {
    "j": { # Jump orbs
        "animations": {
            "default": {
                "path": "res/tiles/animated/jump_orb/idle.png",
                "delay": 10 # Delay between frames
            },
            "struck": {
                "path": "res/tiles/animated/jump_orb/struck.png",
                "delay": 10
            }
        },

        "mask": "res/tiles/animated/jump_orb/mask.png" # Used for pixel perfect collision
    },

    "g": { # Gravity orbs
        "animations": {
            "default": {
                "path": "res/tiles/animated/gravity_orb/idle.png",
                "delay": 5
            },
            "struck": {
                "path": "res/tiles/animated/gravity_orb/struck.png",
                "delay": 10
            }
        },

        "mask": "res/tiles/animated/gravity_orb/mask.png"
    },

    "c": { # Crystals
        "animations": {
            "default": {
                "path": "res/tiles/animated/crystal/idle.png",
                "delay": 8
            },
            "struck": {
                "path": "res/tiles/animated/crystal/collected.png",
                "delay": 10
            }
        },

        "mask": "res/tiles/animated/crystal/mask.png"
    }
}

PLAYER_ANIMATIONS = {
    "idle": {
        "path": "res/characters/player/idle.png",
        "delay": 25
    },
    "walk": {
        "path": "res/characters/player/walk.png",
        "delay": 7
    }
}
PLAYER_WIDTH = 8

ELLIPSE_ANIMATIONS = {
    "idle": {
        "path": "res/characters/ellipse/idle.png",
        "delay": 20
    },
    "walk": {
        "path": "res/characters/ellipse/walking.png",
        "delay": 7
    }
}

CORLEN_ANIMATIONS = {
    "idle": {
        "path": "res/characters/corlen/idle.png",
        "delay": 27
    },
    "walk": {
        "path": "res/characters/corlen/walking.png",
        "delay": 7
    }
}

BEQUE_ANIMATIONS = {
    "idle": {
        "delay": 6,
        "path": "res/characters/beque/idle.png",
        "frames": 4
    },
    "attack": {
        "delay": 5,
        "path": "res/characters/beque/walking.png",
        "frames": 3
    }
}

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