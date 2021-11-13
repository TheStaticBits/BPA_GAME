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
    return min[0] <= vect[0] < max[0] and min[1] <= vect[1] < max[1]


def save_room(saveLevel, saveRoom, tiles):
    levels = load_levels()
    
    with open("levels.txt", "w") as file:
        for levelNumber, level in enumerate(levels):
            if levelNumber != 0:
                file.write(constants.LEVEL_SEPARATOR)
            
            for roomNumber, room in enumerate(level):
                if roomNumber != 0:
                    file.write(constants.ROOM_SEPARATOR)

                iterator = tiles if saveLevel == levelNumber and saveRoom == roomNumber else room

                for rowNumber, row in enumerate(iterator):
                    for tile in row:
                        file.write(str(tile))
            
                    if rowNumber != len(iterator) - 1:
                        file.write("\n")