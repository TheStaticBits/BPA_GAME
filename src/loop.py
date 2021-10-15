import pygame

import src.window

# Initializing Pygame
pygame.init()

class Loop:
    def __init__(self):
        self.window = src.window.Window()
    
    def update(self):
        self.window.update_inputs()
    
    def run_game(self):
        while not self.window.closeWindow:
            self.window.flip()

            self.update()