import pygame
from time import sleep
import threading

import src.window
import src.playing


# Initializing Pygame
pygame.init()

class Loop:
    def __init__(self):
        self.window = src.window.Window()
        self.playing = src.playing.Playing()

        self.scene = "playing"

        self.framerate = 0


    def run_framerate(self):
        while True:
            sleep(1)
            print(self.framerate, "FPS")
            self.framerate = 0


    def run_game(self):
        framerate = threading.Thread(target=self.run_framerate, args=(), daemon=True)
        framerate.start()

        while not self.window.closeWindow:
            self.window.flip()

            self.framerate += 1

            self.update()
            self.render()


    def update(self):
        self.window.update_inputs()

        if self.scene == "playing":
            self.playing.update(self.window.inputs, self.window.mousePos, self.window.mousePressed)
    
    
    def render(self):
        if self.scene == "playing":
            self.playing.render(self.window.miniWindow)