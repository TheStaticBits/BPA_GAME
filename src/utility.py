"""
This file contains functions for things such as saving and loading, loading spritesheets, and more.
"""

import pygame
import time
import math
import sqlite3
import os
import win32api
import logging
import smtplib, ssl
import json
import base64

import src.constants as constants
import src.animation

def setup_loggers():
    """Setting up root logger (and default configuration for future loggers)"""
    rLogger = logging.getLogger("") # Creating root logger
    rLogger.setLevel(logging.DEBUG) # Sets the level to debug so all logs will show
    # Setting up formatters. Console format is simpler
    fileFormatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")
    consoleFormatter = logging.Formatter("%(levelname)s:%(name)s - %(message)s")
    # If the folder that the event.log is in does not exist, create it
    paths = constants.EVENT_LOG_PATH.split("/")
    if not os.path.exists(paths[0]):
        os.makedirs(paths[0])
    # Creating handlers
    handler = logging.FileHandler(constants.EVENT_LOG_PATH)
    console = logging.StreamHandler()
    # Setting formatters
    handler.setFormatter(fileFormatter)
    console.setFormatter(consoleFormatter)
    # Adding handlers
    rLogger.addHandler(handler)
    rLogger.addHandler(console)


# Locks a number to 1, 0, or -1 and returns that number
def lock_neg1_zero_pos1(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0


# Gets a file from the filePath
def get_file(filePath) -> str:
    with open(filePath, "r") as file:
        text = file.read()
    
    return text


# Finds the angle from one point to the next in radians
def angle_to(pos1, pos2) -> float:
    xDiff = pos2[0] - pos1[0]
    yDiff = pos2[1] - pos1[1]

    angle = math.atan2(yDiff, xDiff)

    return angle


# Finds the distance between two points using the Pythagorean Theorem
def distance_to(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


# Finds the last item of a type given in a list and returns the index of the item
def find_last_item(list, item) -> int:
    for i in range(len(list) - 1, -1, -1):
        if list[i] == item:
            return i


# Loads the levels from a given path
def load_levels(levelPath) -> list:
    file = get_file(levelPath)

    levelData = []

    # Splits the string into a list of levels
    levels = file.split(constants.LEVEL_SEPARATOR)

    returnLevels = [] # Levels to be returned

    for level in range(len(levels)):
        # Splits the levels into lists of rooms
        levels[level] = levels[level].split(constants.ROOM_SEPARATOR)
        
        if level % 2 == 0: # If the level index is even, this means this is data for a level, not an actual level
            # Takes something like:
            # background = g
            # music = yes
            # And turns it into a dictionary

            levelData.append({})

            allDat = levels[level][0]
            allDat = allDat.split("\n")

            try:
                for dataBit in allDat:
                    if dataBit != "":
                        dataBit = dataBit.split(constants.ASSIGNMENT_SEPARATOR)
                        levelData[level // 2][dataBit[0]] = dataBit[1]
            
            except IndexError:
                raise Exception(f"Level data is not formatted correctly\nIn level {level // 2}\n{allDat}")


        else: # If it's the contents of the level
            for room in range(len(levels[level])):
                # Splits the rooms into lists of rows
                levels[level][room] = levels[level][room].split("\n")

                for row in range(len(levels[level][room])):
                    # Splits the row into individual characters, the tiles
                    levels[level][room][row] = list(levels[level][room][row])
            
            returnLevels.append(levels[level])
    
    return returnLevels, levelData


# Saves the room to the levels.txt file
# This is for editing, will probably NOT be included in the final game
def save_room(
    saveLevel, # Level number of the room being saved
    saveRoom, # Room number of the room being saved
    tiles, # The list of tiles that the room is being changed to
    filePath
    ):
    levels, levelData = load_levels(filePath)
    
    with open(constants.LEVELS_PATH, "w") as file:
        # Iterating through the levels
        for levelNumber, level in enumerate(levels):
            if levelNumber != 0: # If the level is not the first level
                file.write(constants.LEVEL_SEPARATOR) # Write level separator to the file

            # Writing the level data
            for key, value in levelData[levelNumber].items():
                file.write("\n" + key + constants.ASSIGNMENT_SEPARATOR + value)
            
            file.write(constants.LEVEL_SEPARATOR)
            
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
        width = None, # Width of each image
        frames = None # Frames in the animation
        # Choose either width or frames
    ): 

    image = pygame.image.load(filePath).convert_alpha() # Loads the spritesheet from a file

    # Calculating the other var based on the given
    if width is None: width = image.get_width() // frames
    else: frames = image.get_width() // width

    result = []

    # Iterates through a range which is the amount of images in the spritesheet
    for count in range(frames):
        frame = pygame.Surface((width, image.get_height()), flags=pygame.SRCALPHA) # Creates a surface for each frame
        
        frame.blit(
            image, 
            (-(count * width), # This moves the spritesheet back enough so that the only frame in the image is the individual frame being saved
            0),
            special_flags = pygame.BLEND_RGBA_MAX
        )

        result.append(frame)
    
    return result
    

# Opens a json file and returns the dictionary
def load_json(filePath) -> dict:
    with open(filePath, "r") as file:
        return json.load(file)


# Checks if a point is between the given minimum and maximums
def check_between(
        vect,
        min,
        max
    ):
    return min[0] <= vect[0] < max[0] and min[1] <= vect[1] < max[1]


# Draws text on the screen with a black one pixel border
def draw_text_with_border(
    window, 
    position, 
    text, 
    textObj, # Font object used to render
    color, 
    borderWidth = 1,
    renderText = None, # Surface with text (if already made)
    backgroundText = None, # Pygame Surface with the background text
    alpha = None
    ):
    if renderText is None:
        renderText = textObj.render(text, False, color)
    
    if backgroundText is None:
        bgText = textObj.render(text, False, constants.BLACK)
    
    textSurf = pygame.Surface((renderText.get_width() + borderWidth * 2, renderText.get_height() + 2), flags = pygame.SRCALPHA) # Creates a surface for the text

    # Goes in a square around the text's position
    # Drawing the background text, which is the border
    for x in (0, borderWidth, borderWidth * 2):
        for y in (0, borderWidth, borderWidth * 2):
            textSurf.blit(bgText, (x, y))
    
    # Drawing normal text on screen above the background text
    textSurf.blit(renderText, (borderWidth, borderWidth))

    if alpha is not None:
        textSurf.set_alpha(alpha)
    
    window.blit(textSurf, (position[0] - borderWidth, position[1] - borderWidth)) # Blits the text to the screen


# Plays music from the music folder in res
def play_music(musicName) -> bool: # Successful or not
    try:
        # Setting up music
        pygame.mixer.music.load(f"{constants.MUSIC_FOLDER}/{musicName}.wav")
        pygame.mixer.music.set_volume(0.2)
        
        # Starting music
        pygame.mixer.music.play(-1)

        return True

    except pygame.error:
        # If there wasn't an audio device found, 
        return False


# Loads a dictionary with the animations, with the keys being the animation's name
def load_animations_dict(animations) -> dict:
    animation = {}
    for name, data in animations.items():
        # Getting either the frames or the width of the animation to load it
        frames = None
        width = None
        if "frames" in data: frames = data["frames"]
        elif "width" in data: width = data["width"]
        else: raise Exception(f"Neither frames nor width in data; unable to load animation \"{name}\"")

        animation[name] = src.animation.Animation(
            data["delay"],
            path = data["path"],
            frames = frames,
            width = width
        )
    return animation


"""
DATABASE HANDLING
"""
# Creates a database assuming that there is none, from the default layout found in constants.py
def create_default_database():
    conn = sqlite3.connect(constants.SAVE_PATH) # Creating a connection
    c = conn.cursor() # Creates the cursor

    # Creates a table in the database
    # Var is the name of the item being stored
    c.execute("CREATE TABLE data (var TEXT, value TEXT)")

    # Sets up the default table with the default save
    for key, value in constants.DEFAULT_SAVE.items():
        c.execute("INSERT INTO data VALUES (?, ?)", 
                    (key, value))

    # Committing and closing
    conn.commit()
    conn.close()


# Loads the save file, creating a default save file if it doesn't exist
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
# Also creates a crash report and reports crashes if the user says yes to doing so
def error_box(error):
    pygame.quit() # Closes window


    # Generating crash report file
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    crashReport = f"Generated at {t}\n\nError:\n{error}"
    crashFilePath = constants.CRASH_REPORT_PATH + t
    
    # Creating crash report folder if it doesn't exist
    if not os.path.exists(constants.CRASH_REPORT_PATH.split("/")[1]):
        os.makedirs(constants.CRASH_REPORT_PATH.split("/")[1])

    # Writing to crash report file
    with open(crashFilePath, "w") as file:
        file.write(crashReport)


    result = win32api.MessageBox(
        None, 
        f"""Game ERROR. This is an unrecoverable state.

Error:
----------------------
{error}----------------------

Would you like to report this crash?""", 
        "ERROR", 
        1
    ) # Generates a popup box with the error

    if result == 1: # If the user wants to report the crash
        with open(constants.EVENT_LOG_PATH, "r") as file: # Opens the file
            contents = file.read() # Grabs the contents of the file
        
        contents = "Subject: Another error\n\n" + contents

        connection = ssl.create_default_context() # Creating a connection
        
        # Decoding password
        password = base64.b64decode("cmVwb3J0dGhvc2VjcmFzaGVz").decode("utf-8")

        with smtplib.SMTP_SSL("smtp.gmail.com", context=connection) as s: # Connecting to the server
            s.login("reporterofcrashes@gmail.com", password)

            s.sendmail("reporterofcrashes@gmail.com", "reporterofcrashes@gmail.com", contents) # Sends the email