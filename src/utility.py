"""
This file contains functions for things such as saving and loading, loading spritesheets, and potentially more.
"""

import pygame
import sqlite3
import os
import win32api
import smtplib, ssl

import src.constants as constants


# Gets a file from the filePath
def get_file(filePath) -> str:
    with open(filePath, "r") as file:
        text = file.read()
    
    return text


# Loads the levels from the levels.txt file
def load_levels() -> list:
    file = get_file("levels.txt")

    # Splits the string into a list of levels
    levels = file.split(constants.LEVEL_SEPARATOR)

    for level in range(len(levels)):
        # Splits the levels into lists of rooms
        levels[level] = levels[level].split(constants.ROOM_SEPARATOR)

        for room in range(len(levels[level])):
            # Splits the rooms into lists of rows
            levels[level][room] = levels[level][room].split("\n")

            for row in range(len(levels[level][room])):
                # Splits the row into individual characters, the tiles
                levels[level][room][row] = list(levels[level][room][row])
    
    return levels


# Saves the room to the levels.txt file
# This is for editing, will probably NOT be included in the final game
def save_room(
    saveLevel, # Level number of the room being saved
    saveRoom, # Room number of the room being saved
    tiles # The list of tiles that the room is being changed to
    ):
    levels = load_levels()
    
    with open("levels.txt", "w") as file:
        # Iterating through the levels
        for levelNumber, level in enumerate(levels):
            if levelNumber != 0: # If the level is not the first level
                file.write(constants.LEVEL_SEPARATOR) # Write level separator to the file
            
            for roomNumber, room in enumerate(level):
                if roomNumber != 0: # If it isn't the first room
                    file.write(constants.ROOM_SEPARATOR) # Write room separator to the file

                iterator = tiles if saveLevel == levelNumber and saveRoom == roomNumber else room # If the current room is the one being changed, set the iterator to the new tiles, otherwise set it to the old room

                # Iterating through the room
                for rowNumber, row in enumerate(iterator):
                    for tile in row: # Iterating through the rows
                        file.write(str(tile)) # Writing the tile
            
                    if rowNumber != len(iterator) - 1: # If it is the end of the row
                        file.write("\n") # Add a new line


# This function assumes the spritesheet is horizontal
# It returns a list of all the frames of the spritesheet
def load_spritesheet(
        filePath, # Path to the file
        width # Width of each image
    ): 

    image = pygame.image.load(filePath).convert_alpha() # Loads the spritesheet from a file

    result = []

    # Iterates through a range which is the amount of images in the spritesheet
    for count in range(image.get_width() // width):
        tempImage = pygame.Surface((width, image.get_height())) # Creates an image the size of one frame
        tempImage.blit(
            image, 
            (-(count * width), # This moves the spritesheet back enough so that the only frame in the image is the individual frame being saved
            0)
        )
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
# Creates a database assuming that there is none, from the default layout found in constants.py
def create_default_database():
    conn = sqlite3.connect(constants.SAVE_PATH) # Creating a connection
    c = conn.cursor() # Creates the cursor

    # Creates a table in the database
    # Var is the name of the item being stored
    c.execute("CREATE TABLE data (var TEXT, value REAL)")

    # Sets up the default table with the default save
    for key, value in constants.DEFAULT_SAVE.items():
        c.execute("INSERT INTO data VALUES (?, ?)", 
                    (key, value))

    # Committing and closing
    conn.commit()
    conn.close()


def load_save() -> dict:
    if os.path.isfile(constants.SAVE_PATH): # If the file exists already
        result = {}

        # Connecting and creating a cursor
        conn = sqlite3.connect(constants.SAVE_PATH)
        c = conn.cursor()
        
        # Grabbing all values from the data table
        data = c.execute("SELECT var, value FROM data").fetchall()

        # Adding all the values to a dictionary
        for obj in data:
            result[obj[0]] = obj[1]

        # Closing and returning the result
        conn.close()
        return result
    
    else: # If the file does not exist yet
        create_default_database() # Creating the default database
        return constants.DEFAULT_SAVE # Returning the default save


# Modifies the save with the corresponding keys and values passed in through the dictionary
def modif_save(dict):
    if os.path.isfile(constants.SAVE_PATH): # If the file doesn't exist
        # Creating a connection and cursor
        conn = sqlite3.connect(constants.SAVE_PATH)
        c = conn.cursor()

        # Iterating through the things to be modified
        for key, value in dict.items():
            # Changing the things to be modified
            c.execute("UPDATE data SET value = ? WHERE var = ?", (value, key))

        # Committing and closing
        conn.commit()
        conn.close()
    
    else: # If the save file doesn't exist
        create_default_database() # Create a default database
        modif_save(dict) # Call this function to modify the changes


# This is the error box which pops up when there is an error
def error_box(error):
    result = win32api.MessageBox(
        None, 
        f"""Game crashed. See saves/events.log for more information.

Error:
----------------------
{error}----------------------

Would you like to report this crash?""", 
        "ERROR", 
        1
    ) # Generates a popup box with the error

    if result: # If the user wants to report the crash
        with open(constants.EVENT_LOG_PATH, "r") as file: # Opens the file
            contents = file.read() # Grabs the contents of the file
        
        contents = "Subject: Another error\n\n" + contents

        connection = ssl.create_default_context() # Creating a connection

        with smtplib.SMTP_SSL("smtp.gmail.com", context=connection) as s: # Connecting to the server
            s.login("reporterofcrashes@gmail.com", "reportthosecrashes") # Logs in (yes the password is here)

            s.sendmail("reporterofcrashes@gmail.com", "reporterofcrashes@gmail.com", contents) # Sends the email