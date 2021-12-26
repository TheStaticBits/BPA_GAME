import pygame
import logging
import os
import traceback
from time import sleep
import threading

import src.window
import src.playing
import src.utility as utility
import src.constants as constants
import src.animation
import src.tile_renderer
import src.cutscenes
import src.boss_level
import src.main_menu
import src.pause_menu

# Initializing Pygame
pygame.init()

"""
This class creates and manages all of the scenes, the window, and the main game loop. 
It also sets up the game.
After the game closes, this class takes all game data and calls a function located in src/utility.py which serializes all of the data to a database.
"""
class Loop():
    # Initializes all of the classes
    def __init__(self):
        utility.setup_loggers()
        self.logger = logging.getLogger(__name__)

        self.scene = "startup"
        self.framerate = 0
        self.errorSettingUp = False

        self.transitionImg = None
        self.transitionMode = None
        self.transitionAlpha = 255

        try:
            self.window = src.window.Window()

            self.startupAnim = src.animation.Animation(
                3, # Amount of frames between each frame of the animation
                path = constants.CTM_LOGO_PATH, 
                width = constants.SCREEN_SIZE[0]
            )
            self.startupSound = pygame.mixer.Sound("res/sound/intro.wav")

            self.cutsceneData = utility.load_json(constants.CUTSCENE_DATA_PATH)
            # Level data is the stuff about the level
            self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)
            self.levelsList = self.gen_levels_list()

            save = self.load_save()

            # Setting up scenes
            self.scenes = {
                "playing": src.playing.Playing(),
                "bossLevel": src.boss_level.BossLevel(),
                "cutscene": src.cutscenes.Cutscenes(self.remove_cutscenes, self.crystals),
                "mainMenu": src.main_menu.MainMenu(save, self.levelsList, self.levelsCompleted, self.crystals, self.remove_cutscenes),
                "pauseMenu": src.pause_menu.PauseMenu()
            }

            self.prevScene = self.scene # For the pause menu resuming
        
        except Exception:
            # logging error and opening error box

            err = traceback.format_exc()
            print(err)
            self.logger.critical(f"ERROR WHILE STARTING UP: {err}")

            utility.error_box(err)

            self.errorSettingUp = True

    
    # Loads a save, while also setting up the crystals and levelsCompleted variables
    def load_save(self) -> dict:
        save = utility.load_save()

        # Converts string of ones and zeros into lists of integers
        self.levelsCompleted = [int(x) for x in list(save["levels"])]
        self.crystals = [int(x) for x in list(save["crystals"])]

        self.level = int(save["level"])
        self.ending = int(save["unlockedEnding"])

        return save


    # Makes a list filled with the type of level the level is
    def gen_levels_list(self):
        levelList = []

        for level in range(len(self.levels)):
            if "cutscene" in self.levelData[level]:
                levelList.append("Cutscene")
            
            elif "boss" in self.levelData[level]:
                levelList.append("Boss Level")
            
            else:
                levelList.append("Normal Level")
        
        return levelList


    # Is run in the background.
    # Manages the framerate and prints it out to the console every second.
    def run_framerate(self):
        while not self.window.closeWindow:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    # This handles the main game loop, along with any errors that occur in the game.
    def run_game(self):
        if not self.errorSettingUp: # If there was no error while setting up
            # Starting FPS counter
            framerate = threading.Thread(target=self.run_framerate, args=(), daemon=True)
            framerate.start()

            self.startupSound.play()

            # Main Loop
            while not self.window.closeWindow:
                try:
                    self.window.flip()

                    self.framerate += 1

                    self.update()
                    self.render()

                except Exception:
                    # handles errors that occured in game
                    # logging and giving an error popup box
                    err = traceback.format_exc()
                    print(err)
                    self.logger.critical(f"ERROR WHILE PLAYING: {err}")

                    utility.error_box(err)
            
            self.save_and_exit()
            
    # Sets the level to completed and adds one to the current level index
    def increment_index(self):
        self.levelsCompleted[self.level] = 1
        self.level += 1


    # Takes a level number and subtracts one for every cutscene before the level number given
    def remove_cutscenes(self, levelNum):
        for testLevel in range(levelNum):
            if self.levelsList[testLevel] == "Cutscene":
                levelNum -= 1
        
        return levelNum
    

    # Restarts the game, creating a new save and updating everything that uses the save data
    def restart(self):
        if os.path.exists(constants.SAVE_PATH):
            os.remove(constants.SAVE_PATH)
            
        self.load_save()
        self.scenes["mainMenu"].update_info(self.level, self.levelsCompleted, self.ending, self.crystals)
        self.scenes["cutscene"].update_crystals(self.crystals)
    

    # Returns a result given a command
    # Checks if there are still missing crystals
    def check_crystals(self, command) -> bool:
        if command == "all crystals":
            return 0 not in self.crystals
        elif command == "not all crystals":
            return 0 in self.crystals
    

    # Sets up transition variables
    def start_transition(self):
        self.transitionImg = self.render().copy()
        self.transitionMode = "into"
        self.transitionAlpha = 255
        

    # This method updates the scene the game is in, along with the window class.
    def update(self):
        self.window.update_inputs()

        if self.transitionImg is not None:
            # Updating transition alpha if currently in a transition
            if self.transitionMode == "into": # Fading to black
                self.transitionAlpha -= constants.TRANSITION_SPEED

                if self.transitionAlpha <= 0: # Reached full dark
                    self.transitionAlpha = constants.TRANSITION_SPEED
                    self.transitionMode = "out"
                    # Gets the new scene
                    self.transitionImg = self.render(withoutTransition = True, draw = False).copy() 
            
            elif self.transitionMode == "out": # Fading out of black
                self.transitionAlpha += constants.TRANSITION_SPEED

                if self.transitionAlpha >= 255:
                    self.transitionImg = None # Stop transition

            return None # Doesn't update anything else while transitioning

        elif self.scene == "startup":
            # Startup animation scene
            if not self.startupAnim.update(): # If the startup animation finished
                self.start_transition()
                self.scene = "mainMenu"
                self.scenes["mainMenu"].start_music()
                del self.startupAnim
        
        elif self.scene == "mainMenu": # Updating main menu
            result = self.scenes["mainMenu"].update(self.window.mousePos, self.window.mousePressed)

            if result is not None:
                if result == "play": # "Play" button pressed
                    self.level = self.scenes["mainMenu"].lvlsIndex
                
                elif result == "newSave": # "Restart" button pressed
                    self.restart()
                
                elif result == "quit":
                    self.window.closeWindow = True
                    return None # Prevents from running the rest of the code

                self.switch_to_new_scene(self.level)
                self.update()

        
        elif self.scene == "pauseMenu": # Updating pause menu
            result = self.scenes["pauseMenu"].update(
                self.window.inputs, 
                self.window.mousePos, 
                self.window.mousePressed
            )

            if result != "pause":
                self.window.inputs["esc"] = False
                
                if result == "resume": # "Resume" button pressed
                    self.scene = self.prevScene
                
                elif result == "restart": # "Restart Level" button pressed
                    self.start_transition()
                    # Resets level
                    self.scene = self.prevScene
                    self.scenes[self.scene].restart_level()
                
                elif result == "mainMenu": # "Main Menu" button pressed
                    self.start_transition()
                    # Sets up main menu
                    self.scene = "mainMenu"
                    self.scenes["mainMenu"].start_music()
                    self.scenes["mainMenu"].update_info(self.level, self.levelsCompleted, self.ending, self.crystals)

                    # Tells these that the music has stopped
                    self.scenes["playing"].music_stopped()
                    self.scenes["bossLevel"].music_stopped()
        
        else:
            # Handles all "playing" scenes such as boss levels, cutscenes, and normal levels
            result = self.scenes[self.scene].update(self.window)

            if result is not None:
                if result == "crystal mid-level": # If the level potentially wants it to move onto the next level when a crystal was collected
                    if self.check_crystals(self.levelData[self.level]["crystal moves on"]):
                        result = "crystal" # Collects the crystal and moves onto the next level
                    else:
                        return None # Doesn't run the rest of the code

                if result == "crystal": # Crystal collected
                    # Gets the crystal id of the level
                    # Getting rid of cutscenes from the level id because cutscenes
                    # don't have crystals
                    if "crystal moves on" not in self.levelData[self.level]:
                        crystalCount = self.remove_cutscenes(self.level)
                        self.crystals[crystalCount] = 1
                
                if result != "restart": # Increments level and switches to new level
                    self.increment_index()
                    self.switch_to_new_scene(self.level)
                
                else: # Restarts game
                    self.restart()
                    self.switch_to_new_scene(self.level)


        if self.scene not in ("startup", "pauseMenu", "mainMenu"): # Scenes without a pause button
            if self.scenes["pauseMenu"].check_for_pause(
                self.window.inputs, 
                self.window.mousePos, 
                self.window.mousePressed
                ): # If the escape button or the pause button has been pressed

                self.prevScene = self.scene

                # Gets the background for the pause menu
                self.scenes[self.scene].render(self.window.miniWindow)
                self.scenes["pauseMenu"].update_background(self.window.miniWindow)
                
                self.scene = "pauseMenu"
    

    # This method renders all objects, based on the current scene 
    def render(self, withoutTransition = False, draw = True) -> "pygame.Surface":
        surf = pygame.Surface(constants.SCREEN_SIZE)

        if self.transitionImg is None or withoutTransition:
            if self.scene == "startup": # Startup animation
                self.startupAnim.render(surf, (0, 0))
            
            else: # Normal scenes
                self.scenes[self.scene].render(surf)

                if self.scene not in ("mainMenu", "pauseMenu"):
                    # Rendering pause button
                    self.scenes["pauseMenu"].render_pause_button(surf)
        
        else: # Render transition
            self.transitionImg.set_alpha(self.transitionAlpha)
            surf.blit(self.transitionImg, (0, 0))
        
        if draw:
            self.window.miniWindow.blit(surf, (0, 0))

        return surf


    # Switches to a new scene based on the level id it's given to switch to
    def switch_to_new_scene(self, level):
        self.start_transition()

        if level >= len(self.levelsList):
            # Sets up main menu
            self.scene = "mainMenu"
            self.scenes["mainMenu"].start_music()
            self.scenes["playing"].music_stopped()
            self.scenes["bossLevel"].music_stopped()

            return None # Exits without running the rest

        # Checking if the level is an ending
        if level >= len(self.levels) - constants.AMOUNT_OF_ENDINGS:
            # If the player hasn't unlocked an ending yet
            if int(utility.load_save()["unlockedEnding"]) == -1:
                # Iterating through from 0 to the amount of endings there are
                for lvl in range(constants.AMOUNT_OF_ENDINGS):
                    # level being checked
                    levelID = len(self.levels) - constants.AMOUNT_OF_ENDINGS + lvl
                    
                    if self.check_crystals(self.levelData[levelID]["ending"]):
                        level += lvl # Setting to that ending
                        self.level = level
                        self.ending = lvl + 1
                        utility.modif_save({"unlockedEnding": lvl + 1}) # Saving the ending
                        self.scenes["mainMenu"].ending = lvl + 1
                        break
            
            else:
                # Setting the level to the ending that was unlocked
                level = len(self.levels) - constants.AMOUNT_OF_ENDINGS + int(utility.load_save()["unlockedEnding"]) - 1


        if self.levelsList[level] == "Normal Level":
            # Sets up normal level
            self.scene = "playing"
            self.scenes["playing"].setup(level, self.crystals, self.remove_cutscenes(level))
            self.scenes["playing"].popup(f"Level {self.remove_cutscenes(level) + 1}")
            self.scenes["bossLevel"].music_stopped()
        
        elif self.levelsList[level] == "Boss Level":
            # Sets up boss level
            self.scene = "bossLevel"
            self.scenes["bossLevel"].setup(self.levelData[level]["boss"], level, self.crystals, self.remove_cutscenes(level))
            self.scenes["bossLevel"].popup(f"Level {self.remove_cutscenes(level) + 1}")
            self.scenes["playing"].music_stopped()

        elif self.levelsList[level] == "Cutscene":
            # Sets up cutscene
            self.scene = "cutscene"
            self.scenes["cutscene"].setup(self.levelData[level]["cutscene"], level)

            # Tells these that the music has stopped
            self.scenes["playing"].music_stopped()
            self.scenes["bossLevel"].music_stopped()


    # This method saves all data to a database for later playing
    def save_and_exit(self):    
        self.logger.info("Saving game state...")

        # Saves the game's data
        utility.modif_save({
            "levels": "".join([str(x) for x in self.levelsCompleted]),
            "level": self.scenes["playing"].level,
            "crystals": "".join([str(x) for x in self.crystals])
        }) 

        self.logger.info("Exiting Pygame...")
        
        # Quits Pygame
        pygame.quit()