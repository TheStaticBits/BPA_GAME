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

            save = utility.load_save()

            self.scenes = {
                "playing": src.playing.Playing(save),
                "bossLevel": src.boss_level.BossLevel(save),
                "cutscene": src.cutscenes.Cutscenes(),
                "mainMenu": src.main_menu.MainMenu(),
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


    def update(self):
        # This method updates the scene the game is in, along with the window class.
        super().update() # Logging

        self.window.update_inputs()


        if self.scene == "playing":
            result = self.scenes["playing"].update(self.window.inputs, self.window.mousePos, self.window.mousePressed)
            
            if result != None: # If the playing class switched to a cutscene
                if result[0] == "cutscene":
                    self.scenes["cutscene"].setup(result[1])
                
                elif result[0] == "bossLevel":
                    self.scenes["bossLevel"].setup(result[1], self.scenes["playing"].level, self.scenes["playing"].room)
                
                self.scene = result[0]
                self.update()
        
        elif self.scene == "cutscene":
            result = self.scenes["cutscene"].update(self.window.inputs)

            if result == False: # If the cutscene ended
                check = self.scenes["playing"].check_for_boss()
                if check is None:
                    self.scene = "playing"
                    self.scenes["playing"].setup()
                
                else:
                    self.scene = "bossLevel"
                    self.scenes["bossLevel"].setup(check, self.scenes["playing"].level, self.scenes["playing"].room)

                    self.update()
        
        elif self.scene == "bossLevel":
            check = self.scenes["bossLevel"].update(self.window.inputs)
            if check != None:
                self.scenes["playing"].level = self.scenes["bossLevel"].level
                self.scenes["playing"].room = 0

                if check == "playing":
                    self.scene = "playing"
                    self.scenes["playing"].setup()
                
                else:
                    self.scenes["cutscene"].setup(check)
                    self.scene = "cutscene"
        
        elif self.scene == "mainMenu":
            check = self.scenes["mainMenu"].update(self.window.mousePos, self.window.mousePressed)

            if check == "start":
                self.check_what_scene()
                self.update()
        
        elif self.scene == "pauseMenu":
            check = self.scenes["pauseMenu"].update(
                self.window.inputs, 
                self.window.mousePos, 
                self.window.mousePressed
            )

            if check != "pause":
                self.window.inputs["esc"] = False
                
                if check == "resume":
                    self.scene = self.prevScene
                    self.scenes[self.scene].start_music()
                
                elif check == "mainMenu":
                    self.scene = "mainMenu"
                    self.scenes["mainMenu"].start_music()


        if self.scenes["pauseMenu"].check_for_pause(self.scene, self.window.inputs):
            if self.scene != "pauseMenu":
                self.prevScene = self.scene

                self.scenes[self.scene].render(self.window.miniWindow)
                self.scenes["pauseMenu"].update_background(self.window.miniWindow)
                
                self.scene = "pauseMenu"
    
    def render(self) -> "pygame.Surface":
        # This method renders all objects, based on the current scene 
        super().render()

        self.scenes[self.scene].render(self.window.miniWindow)

        return self.window.miniWindow


    def check_what_scene(self):
        cutsceneCheck = self.scenes["playing"].check_for_cutscene()
        bossCheck = self.scenes["playing"].check_for_boss()

        if cutsceneCheck != None and self.scenes["playing"].room == 0:
            # If there was a cutscene where the player was when they closed the game
            self.scenes["cutscene"].setup(cutsceneCheck)
            self.scene = "cutscene"
        
        elif bossCheck != None:
            self.scene = "bossLevel"
            self.scenes["bossLevel"].setup(bossCheck, self.scenes["playing"].level, self.scenes["playing"].room)
        
        else:
            self.scene = "playing"
            self.scenes["playing"].start_music()


    def save_and_exit(self):
        # This method saves all data to a database for later playing
        
        self.logger.info("Saving game state...")

        # Saves the game's data
        utility.modif_save({
            "playerX": self.scenes["playing"].player.rect.x,
            "playerY": self.scenes["playing"].player.rect.y,
            "playerYVelocity": self.scenes["playing"].player.yVelocity,
            "playerXVelocity": self.scenes["playing"].player.xVelocity,
            "globalGravity": self.scenes["playing"].gravityDir,
            "level": self.scenes["playing"].level,
            "room": self.scenes["playing"].room,
            "crystals": "".join([str(x) for x in self.scenes["playing"].crystals])
        }) 

        self.logger.info("Exiting Pygame...")
        
        # Quits Pygame
        pygame.quit()