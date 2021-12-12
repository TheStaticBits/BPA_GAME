import pygame
import traceback
from time import sleep
import threading

import src.window
import src.playing
import src.utility as utility
import src.scene_base
import src.constants as constants
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
class Loop(src.scene_base.SceneBase):
    def __init__(self):
        # Initializes all of the classes, with error handling.
        super().__init__(__name__)

        self.scene = "mainMenu"
        self.framerate = 0
        self.errorSettingUp = False

        try:
            self.window = src.window.Window()

            self.cutsceneData = utility.load_json(constants.CUTSCENE_DATA_PATH)
            self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)
            self.levelsList = self.gen_levels_list()

            save = utility.load_save()

            self.levelsCompleted = list(save["levels"])
            self.level = int(save["level"])
            self.crystals = [int(x) for x in list(save["crystals"])] # Converting the saved string to a list of ints

            self.scenes = {
                "playing": src.playing.Playing(self.levelsList),
                "bossLevel": src.boss_level.BossLevel(self.levelsList),
                "cutscene": src.cutscenes.Cutscenes(),
                "mainMenu": src.main_menu.MainMenu(save, self.levelsList),
                "pauseMenu": src.pause_menu.PauseMenu()
            }

            self.prevScene = self.scene # For the pause menu resuming

            self.scenes["mainMenu"].start_music()
        
        except Exception:
            err = traceback.format_exc()
            print(err)
            self.logger.critical("ERROR WHILE STARTING UP: ")
            self.logger.critical(err)

            utility.error_box(err)

            self.errorSettingUp = True


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


    def run_framerate(self):
        # Is run in the background.
        # Manages the framerate and prints it out to the console every second.
        while not self.window.closeWindow:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    def run_game(self):
        # This handles the main game loop, along with any errors that occur in the game.
        if not self.errorSettingUp: # If there was no error while setting up
            # Starting FPS counter
            framerate = threading.Thread(target=self.run_framerate, args=(), daemon=True)
            framerate.start()

            try:
                while not self.window.closeWindow:
                    with open(constants.EVENT_LOG_PATH, "w"):
                        # Clearing the events.log file
                        pass

                    self.window.flip()

                    self.framerate += 1

                    self.update()
                    self.render()

                self.save_and_exit()

            except Exception:
                err = traceback.format_exc()
                print(err)
                self.logger.critical("ERROR WHILE PLAYING: ")
                self.logger.critical(err)

                utility.error_box(err)


    def increment_index(self):
        self.levelsCompleted[self.level] = 1
        self.level += 1


    def remove_cutscenes(self, levelNum):
        level = levelNum

        for lvl in range(levelNum):
            if self.levelsList[lvl] == "Cutscene":
                level -= 1
        
        return level


    def update(self):
        # This method updates the scene the game is in, along with the window class.
        super().update() # Logging

        self.window.update_inputs()
        
        if self.scene == "mainMenu":
            result = self.scenes["mainMenu"].update(self.window.mousePos, self.window.mousePressed)


            if result is not None:
                if result == "start":
                    level = self.level
                
                elif result == "play":
                    level = self.scenes["mainMenu"].lvlsIndex

                self.switch_to_new_scene(level)
                self.update()

        
        elif self.scene == "pauseMenu":
            result = self.scenes["pauseMenu"].update(
                self.window.inputs, 
                self.window.mousePos, 
                self.window.mousePressed
            )

            if result != "pause":
                self.window.inputs["esc"] = False
                
                if result == "resume":
                    self.scene = self.prevScene
                
                elif result == "restart":
                    self.scene = self.prevScene
                    self.scenes[self.scene].restart_level()
                
                elif result == "mainMenu":
                    self.scene = "mainMenu"
                    self.scenes["mainMenu"].start_music()
                    self.scenes["mainMenu"].change_level(self.level)
        
        else:
            # Handles all "playing" scenes such as boss levels, cutscenes, and normal levels
            result = self.scenes[self.scene].update(self.window)

            if result is not None:
                if result == "crystal":
                    crystalCount = self.remove_cutscenes(self.level)
                    self.crystals[crystalCount] = 1

                self.increment_index()
                self.switch_to_new_scene(self.level)


        if self.scenes["pauseMenu"].check_for_pause(self.scene, self.window.inputs):
            if self.scene != "pauseMenu" and self.scene != "mainMenu":
                self.prevScene = self.scene

                self.scenes[self.scene].render(self.window.miniWindow)
                self.scenes["pauseMenu"].update_background(self.window.miniWindow)
                
                self.scene = "pauseMenu"
    

    def render(self) -> "pygame.Surface":
        # This method renders all objects, based on the current scene 
        super().render()

        self.scenes[self.scene].render(self.window.miniWindow)

        return self.window.miniWindow


    def switch_to_new_scene(self, level):
        if self.levelsList[level] == "Normal Level":
            self.scene = "playing"
            self.scenes["playing"].setup(level, self.crystals[self.remove_cutscenes(level)])
        
        elif self.levelsList[level] == "Boss Level":
            self.scene = "bossLevel"
            self.scenes["bossLevel"].setup(self.levelData[level]["boss"], level, self.crystals[self.remove_cutscenes(level)])

        elif self.levelsList[level] == "Cutscene":
            self.scene = "cutscene"
            self.scenes["cutscene"].setup(self.levelData[level]["cutscene"], level)


    def save_and_exit(self):
        # This method saves all data to a database for later playing
        
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