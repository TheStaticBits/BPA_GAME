"""
This file contains functions for things such as saving and loading, loading spritesheets, and potentially more.
"""

import pygame

import src.constants

def get_file(filePath) -> str:
    with open(filePath, "r") as file:
        text = file.read()
    
    return text


def load_levels() -> list:
    file = get_file("levels.txt")

    file = file.split(constants.LEVEL_SEPARATOR)

    for level in file:
        level = level.split(constants.ROOM_SEPARATOR)

        for room in level:
            room = room.split("\n")

            for row in room:
                row = list(row)
    
    return file


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
        tempImage.blit((-count * width, 0))
        result.append(tempImage)
    
    return result