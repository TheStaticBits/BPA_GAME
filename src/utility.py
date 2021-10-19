"""
This file contains functions for things such as saving and loading, loading spritesheets, and potentially more.
"""

import pygame

def get_file() -> str:
    with open("save.txt", "r") as file:
        text = file.read()
    
    return text


def get_level() -> int:
    file = get_file()


def get_position():
    file = get_file()


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