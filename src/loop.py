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

# Initializing Pygame
pygame.init()

class Loop(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        self.scene = "playing"
        self.framerate = 0
        self.error = False

        try:
            self.window = src.window.Window()

            save = utility.load_save()
            self.playing = src.playing.Playing(save)
            
            try:
                # Setting up music
                pygame.mixer.music.load("res/sound/ThereIsSomethingV2.wav")
                pygame.mixer.music.set_volume(0.2)
                
                # Starting music
                pygame.mixer.music.play(-1)

            except pygame.error:
                # If there wasn't an audio device found, 
                print("ERROR: Audio output device not found.")
                self.logger.warning("Audio output device not found.")
        
        except Exception:
            err = traceback.format_exc()
            print(err)
            self.logger.critical("ERROR WHILE STARTING UP: ")
            self.logger.critical(err)

            utility.error_box(err)

            self.error = True


    def run_framerate(self):
        while True:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    def run_game(self):
        if not self.error:
            # Starting FPS counter
            framerate = threading.Thread(target=self.run_framerate, args=(), daemon=True)
            framerate.start()

            try:
                while not self.window.closeWindow:
                    # Clearing the events.log file
                    with open(constants.EVENT_LOG_PATH, "w"):
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
    
    
    def save_and_exit(self):
        self.logger.info("Saving game state...")

        # Saves the player's position, level, and room
        utility.modif_save({
            "playerX": self.playing.player.rect.x,
            "playerY": self.playing.player.rect.y,
            "playerYVelocity": self.playing.player.yVelocity,
            "playerXVelocity": self.playing.player.xVelocity,
            "level": self.playing.level,
            "room": self.playing.room,
            "crystals": "".join([str(x) for x in self.playing.crystals])
        }) 

        self.logger.info("Exiting Pygame...")
        
        # Quits Pygame
        pygame.quit()


    def update(self):
        super().update()

        self.window.update_inputs()

        if self.scene == "playing":
            self.playing.update(self.window.inputs, self.window.mousePos, self.window.mousePressed)
    
    
    def render(self):
        super().render()

        if self.scene == "playing":
            self.playing.render(self.window.miniWindow)