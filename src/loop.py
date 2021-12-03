import pygame
import logging
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

        self.scene = "playing"
        self.framerate = 0
        self.error = False

        try:
            self.window = src.window.Window()

            save = utility.load_save()

            self.playing = src.playing.Playing(save)

            self.cutscene = src.cutscenes.Cutscenes()
            self.bossLevel = src.boss_level.BossLevel()

            check = self.playing.check_for_cutscene()

            if check != None and self.playing.room == 0:
                # If there was a cutscene where the player was when they closed the game
                self.cutscene.setup(check)
                self.scene = "cutscene"
            
            else:
                self.playing.start_music()
        
        except Exception:
            err = traceback.format_exc()
            print(err)
            self.logger.critical("ERROR WHILE STARTING UP: ")
            self.logger.critical(err)

            utility.error_box(err)

            self.error = True


    def run_framerate(self):
        # Is run in the background.
        # Manages the framerate and prints it out to the console every second.
        while True:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    def run_game(self):
        # This handles the main game loop, along with any errors that occur in the game.
        if not self.error:
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
            result = self.playing.update(self.window.inputs, self.window.mousePos, self.window.mousePressed)
            
            if result != None: # If the playing class switched to a cutscene
                if result[0] == "cutscene":
                    self.cutscene.setup(result[1])
                
                elif result[0] == "boss":
                    self.bossLevel.setup(result[1], self.playing.level, self.playing.room)
                
                self.scene = result[0]
        
        if self.scene == "cutscene":
            result = self.cutscene.update(self.window.inputs)

            if result == False: # If the cutscene ended
                self.scene = "playing"
                self.playing.load_room()
                self.playing.start_music()
        
        if self.scene == "boss":
            self.bossLevel.update(self.window.inputs)
    
    
    def render(self):
        # This method renders all objects, based on the current scene 
        super().render()

        if self.scene == "playing":
            self.playing.render(self.window.miniWindow)
        
        elif self.scene == "cutscene":
            self.cutscene.render(self.window.miniWindow)
    

    def save_and_exit(self):
        # This method saves all data to a database for later playing
        
        self.logger.info("Saving game state...")

        # Saves the game's data
        utility.modif_save({
            "playerX": self.playing.player.rect.x,
            "playerY": self.playing.player.rect.y,
            "playerYVelocity": self.playing.player.yVelocity,
            "playerXVelocity": self.playing.player.xVelocity,
            "globalGravity": self.playing.gravityDir,
            "level": self.playing.level,
            "room": self.playing.room,
            "crystals": "".join([str(x) for x in self.playing.crystals])
        }) 

        self.logger.info("Exiting Pygame...")
        
        # Quits Pygame
        pygame.quit()