import pygame
from time import sleep
import threading

import src.window
import src.playing
import src.utility as utility

# Initializing Pygame
pygame.init()

class Loop:
    def __init__(self):
        self.window = src.window.Window()

        save = utility.load_save()
        self.playing = src.playing.Playing(save)

        self.scene = "playing"

        self.framerate = 0

        # Setting up music
        pygame.mixer.music.load("res/sound/OneLastDayInParadiseV2.wav")
        pygame.mixer.music.set_volume(0.2)


    def run_framerate(self):
        while True:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    def run_game(self):
        # Starting FPS counter
        framerate = threading.Thread(target=self.run_framerate, args=(), daemon=True)
        framerate.start()

        # Starting music
        pygame.mixer.music.play(-1)

        while not self.window.closeWindow:
            self.window.flip()

            self.framerate += 1

            self.update()
            self.render()
    
    
    def save_and_exit(self):
        # Saves the player's position, level, and room
        utility.modif_save({
            "playerX": self.playing.player.rect.x,
            "playerY": self.playing.player.rect.y,
            "playerVelocity": self.playing.player.yVelocity,
            "level": self.playing.level,
            "room": self.playing.room,
        }) 

        # Quits Pygame
        pygame.quit()


    def update(self):
        self.window.update_inputs()

        if self.scene == "playing":
            self.playing.update(self.window.inputs, self.window.mousePos, self.window.mousePressed)
    
    
    def render(self):
        if self.scene == "playing":
            self.playing.render(self.window.miniWindow)