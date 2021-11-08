"""
This file contains functions for things such as saving and loading, loading spritesheets, and potentially more.
"""

import pygame

import src.constants as constants

def get_file(filePath) -> str:
    with open(filePath, "r") as file:
        text = file.read()
    
    return text


def load_levels() -> list:
    file = get_file("levels.txt")

    levels = file.split(constants.LEVEL_SEPARATOR)

    for level in range(len(levels)):
        levels[level] = levels[level].split(constants.ROOM_SEPARATOR)

        for room in range(len(levels[level])):
            levels[level][room] = levels[level][room].split("\n")

            for row in range(len(levels[level][room])):
                levels[level][room][row] = list(levels[level][room][row])
    
    return levels


def get_level() -> int:
    file = get_file("save.txt")


def get_position():
    file = get_file("save.txt")


# This function assumes the spritesheet is horizontal
def load_spritesheet(
        filePath, 
        width # Width of each image
    ): 

    image = pygame.image.load(filePath).convert_alpha()

    result = []

    for count in range(image.get_width() // width):
        tempImage = pygame.Surface((width, image.get_height()))
        tempImage.blit(image, (-(count * width), 0))
        result.append(tempImage)
    
    return result


def check_between(
        vect,
        min,
        max
    ):
    return vect[0] >= min[0] and vect[0] <= max[0] and vect[1] >= min[1] and vect[1] <= max[1]