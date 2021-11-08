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
JUMP_FORCE = 3 # Upward force
GRAVITY = 0.2 # Downward force
MOVEMENT_SPEED = 2

# This is the key used for the tiles.
# The number 1 means that there should be a tile,
# The number 0 means that there shouldn't be a tile,
# The number 2 means that it doesn't matter if there's a tile there.
TILESET_KEY = [
    ((1, 1, 1),
     (1, 1, 1),
     (1, 1, 1)),

    ((2, 0, 2),
     (1, 1, 1),
     (1, 1, 1)),

    ((2, 1, 1),
     (0, 1, 1),
     (2, 1, 1)),
     
    ((1, 1, 1),
     (1, 1, 1),
     (2, 0, 2)),

    ((1, 1, 2),
     (1, 1, 0),
     (1, 1, 2)),
    
    ((2, 0, 2),
     (0, 1, 1),
     (2, 1, 1)),
     
    ((2, 1, 1),
     (0, 1, 1),
     (2, 0, 2)),
     
    ((1, 1, 2),
     (1, 1, 0),
     (2, 0, 2)),
     
    ((2, 0, 2),
     (1, 1, 0),
     (1, 1, 2)),
     
    ((0, 1, 1),
     (1, 1, 1),
     (1, 1, 1)),
     
    ((1, 1, 1),
     (1, 1, 1),
     (0, 1, 1)),

    ((1, 1, 1),
     (1, 1, 1),
     (1, 1, 0)),
     
    ((1, 1, 0),
     (1, 1, 1),
     (1, 1, 1)), 
    
    ((0, 1, 0),
     (1, 1, 1),
     (1, 1, 1)),
      
    ((0, 1, 1),
     (1, 1, 1),
     (0, 1, 1)),
     
    ((1, 1, 1),
     (1, 1, 1),
     (0, 1, 0)),
     
    ((1, 1, 0),
     (1, 1, 1),
     (1, 1, 0)),
      
    ((2, 1, 2),
     (1, 1, 1),
     (2, 1, 2)),
    
    ((2, 0, 2),
     (0, 1, 0),
     (2, 0, 2)),
     
    ((2, 0, 2),
     (1, 1, 1),
     (1, 1, 0)),
      
    ((2, 0, 2),
     (1, 1, 1),
     (0, 1, 0)),
    
    ((2, 0, 2),
     (1, 1, 1),
     (0, 1, 1)),
    
    ((1, 1, 0),
     (1, 1, 1),
     (2, 0, 2)),

    ((0, 1, 0),
     (1, 1, 1),
     (2, 0, 2)),

    ((0, 1, 1),
     (1, 1, 1),
     (2, 0, 2)),
       
    ((2, 0, 2),
     (0, 1, 0),
     (2, 1, 2)),
       
    ((2, 1, 2),
     (0, 1, 0),
     (2, 1, 2)),
       
    ((2, 1, 2),
     (0, 1, 0),
     (2, 0, 2)),
       
    ((2, 0, 2),
     (0, 1, 1),
     (2, 0, 2)),
       
    ((2, 0, 2),
     (1, 1, 1),
     (2, 0, 2)),
       
    ((2, 0, 2),
     (1, 1, 0),
     (2, 0, 2)),
]