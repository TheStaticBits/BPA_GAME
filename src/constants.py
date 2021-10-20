import pygame

FPS = 60 # Frame rate of the screen

TILE_SIZE = (16, 16)
SCREEN_TILE_SIZE = (24, 14) # Amount of tiles on the screen by X and Y

LEVEL_SEPARATOR = "\n------------------------\n"
ROOM_SEPARATOR = "\n||||||||||||||||||||||||\n"

PX_SCALE_FACTOR = 3 # This is the scale factor of everything being rendered to the screen

LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
UP_KEYS = (pygame.K_UP, pygame.K_w)