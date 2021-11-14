import pygame

import src.utility as utility

class Animation:
    def __init__(
        self, 
        path, # Path of the image
        width, # Width of one frame
        delay, # Delay between frames
        ):
        self.images = utility.load_spritesheet(path, width)

        self.timer = 0
        self.frame = 0

        self.delay = delay
    
    def update(self) -> bool:
        self.timer += 1

        if self.timer >= self.delay:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = 0
                return False # If the animation is finished

        return True
    
    def render(self, window, position):
        window.blit(self.images[self.frame], position)