import pygame

import src.window
import src.playing

# Initializing Pygame
pygame.init()

class Loop:
    def __init__(self):
        self.window = src.window.Window()
        self.playing = src.playing.Playing()
    
    def run_game(self):
        while not self.window.closeWindow:
            self.window.flip()

            self.update()
            self.render()

    def update(self):
        self.window.update_inputs()
        self.playing.update()
    
    
    def render(self):
        self.playing.render()