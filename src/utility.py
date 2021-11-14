"""
This file contains functions for things such as saving and loading, loading spritesheets, and potentially more.
"""

import pygame
import sqlite3
import os

import src.constants as constants


# Gets a file from the filePath
def get_file(filePath) -> str:
    with open(filePath, "r") as file:
        text = file.read()
    
    return text


# Loads the levels from the levels.txt file
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


# Saves the room to the levels.txt file
# This is for editing, will probably NOT be included in the final game
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

"""
DATABASE HANDLING
"""
def create_default_database():
    conn = sqlite3.connect(constants.SAVE_PATH)
    c = conn.cursor()

    c.execute("CREATE TABLE data (var TEXT, value REAL)")

    for key, value in constants.DEFAULT_SAVE.items():
        c.execute("INSERT INTO data VALUES (?, ?)", 
                    (key, value))

    conn.commit()
    conn.close()


def load_save() -> dict:
    if os.path.isfile(constants.SAVE_PATH):
        result = {}

        conn = sqlite3.connect(constants.SAVE_PATH)
        c = conn.cursor()
        
        data = c.execute("SELECT var, value FROM data").fetchall()

        for obj in data:
            result[obj[0]] = obj[1]

        conn.close()
        return result
    
    else:
        create_default_database()
        return constants.DEFAULT_SAVE


# Modifies the save with the corresponding keys and values passed in through the dictionary
def modif_save(dict):
    if os.path.isfile(constants.SAVE_PATH):
        conn = sqlite3.connect(constants.SAVE_PATH)
        c = conn.cursor()

        for key, value in dict.items():
            c.execute("UPDATE data SET value = ? WHERE var = ?", (value, key))

        conn.commit()
        conn.close()
    
    else:
        create_default_database()
        modif_save(dict)