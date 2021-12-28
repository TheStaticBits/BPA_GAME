import pygame

import src.utility as utility

"""  File paths for multiple things  """
SAVE_PATH = "saves/save.db"
EVENT_LOG_PATH = "saves/events.log"
CRASH_REPORT_PATH = "saves/crash"

CTM_LOGO_PATH = "res/ui/CTM_logo.png" # Cognitive Thought Media (Company Logo)
TIN_LOGO_PATH = "res/ui/TIN_logo.png" # There Is Nothing (Game Logo)

FONT_PATH = "res/font/monogram.ttf"
FONT_SIZE = 15

LEVELS_PATH = "data/levels.txt"

CUTSCENE_DATA_PATH = "data/cutscenes.json"

MAIN_MENU_LEVEL_PATH = "data/menu_level.txt"

EMAIL_PWD_PATH = "data/emailpassword.txt"

MUSIC_FOLDER = "res/sound/music"

SCREEN_SHADOW_PATH = "res/game/shadow.png"

CRYSTAL_CHECK_PATH = "res/ui/crystal_check.png"
CRYSTAL_X_PATH = "res/ui/crystal_x.png"

ARROW_PATH = "res/ui/arrow.png"

PAUSE_BUTTON_PATH = "res/ui/pause_button.png"


# Level editing in normal levels
LEVEL_EDITING = True
# Controls for level editing in normal levels:
# Right click: Changes tile the mouse is hovering over to air
# Middle click: Copies tile the mouse is hovering over, so it places that tile when you left click
# Left click: Fills the tile the mouse is hovering over to the tile that you have copied
# Space: Save room (BE CAREFUL, if you have collected the crystal in the given level, it may REMOVE the crystal from the level data) 

BUTTON_HIGHLIGHT_SPEED = 10 # The higher this goes, the slower buttons fills up when hovering a mouse over it.

SCREEN_SHAKE_POWER = 2 # How intense screenshakes are (in cutscenes)

POPUP_TEXT_DURATION = 60 # How long the popup text stays on screen until it starts fading
POPUP_TEXT_FADE_SPEED = 4 # How quickly the popup text fades out

TRANSITION_SPEED = 32 # Transition speed for general transitions

# Color constants for easy access
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
    "levels": "111111111111111111111111111111", # Levels unlocked
    "level": 0, # Selected level
    "crystals": "00000000000000000000", # Crystals unlocked in normal levels
    "unlockedEnding": -1, # Ending unlocked
    "speedrunHighscore": 0 # Speedrun highscore!
}

AMOUNT_OF_ENDINGS = 2 # How many endings there are

# Solid Tiles
# first value indicating the string in the level layout
# second value is the folder name of the tile
# (solid tiles are stored in res/tiles/solid/[tile name]/)
TILE_KEYS = {
    "w": "default",
    "o": "crystal",
    "s": "star",
    "d": "dirt",
    "e": "blank",
    "b": "darkness",
    "u": "blumech",
    "l": "blue",
    "W": "white"
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

HOLDABLE_TILES = (
    "m", # Gravity button
    "g"
)

# Other tiles
SPIKE_PATH = "res/tiles/solid/spike/dark.png"
BRIGHT_SPIKE_PATH = "res/tiles/solid/spike/bright.png"
SPIKE_ROTATIONS = {
    "^": 0,
    "<": 90,
    "v": 180,
    ">": 270
}

# Tiles which when used as the background tile, use a bright spike
TILES_USING_BRIGHT_SPIKE = (
    "e",
    "b"
)
# Tiles that do not have shading when used as a background tile
TILES_WITHOUT_SHADING = (
    "W"
)
# Animated tiles whos animations don't flip when gravity changes
NO_ROTATE_TILES = (
    "m"
)

# These tiles have animations
TILES_WITH_ANIMATIONS = utility.load_json("res/tiles/animated/anim_dat.json")

# Animation data for the Player, Ellipse, and Corlen
PLAYER_ANIMATIONS = utility.load_json("res/characters/player/animations.json")
ELLIPSE_ANIMATIONS = utility.load_json("res/characters/ellipse/animations.json")
CORLEN_ANIMATIONS = utility.load_json("res/characters/corlen/animations.json")

PLAYER_WIDTH = 8 # In pixels

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

LAZER_SPEED = 2 # Pixels moved per frame
LAZER_LENGTH = 20 # Length of each lazer in pixels
LAZER_COLOR = (255, 255, 0) # Color of the lazer

# Big Bite Boss constants
BIG_BITE_ANIM_PATH = "res/characters/big_bite/anim.png"
BIG_BITE_ATTACK_FRAME = 3 # The frame number in the animation in which collisions are checked between the player and the boss
BIG_BITE_TOTAL_FRAMES = 5
BIG_BITE_DELAY = 15 # The delay between frames in the animation, in game frames (60 frames per second)
BIG_BITE_ATTACK_DELAY = (5, 40) # The delay between each attack in frames. It is randomly chosen between these two numbers

RED_STARE_ANIMATIONS = utility.load_json("res/characters/red_stare/animations.json")
RED_STARE_COOLDOWN = 50 # Frames between each time it pops up from below the screen to throw its mouth
RED_STARE_POPUP_RANGE = 100 # Pixels in each direction from the player's X that it can popup at (it's random)
RED_STARE_POPUP_SPEED = 1 # How many pixels it moves to popup per frame
RED_STARE_MOUTH_OFFSET = (23, -21) # The offset of the mouth from the top left of the sprite
RED_STARE_MOUTH_SPEED = 1

# Gravity beam data
GRAV_BEAM_PATH = "res/game/grav_beam.png"
GRAV_BEAM_DELAY = 2 # Delay between each frame of the beam
GRAV_BEAM_WIDTH = 8 # Width of the beam

GRAV_BEAM_TILE_Y_POS = SCREEN_TILE_SIZE[1] / 2