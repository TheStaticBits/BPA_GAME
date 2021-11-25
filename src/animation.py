import pygame

import src.utility as utility

class Animation:
    def __init__(
        self, 
        delay, # Delay between frames
        path = None, # Path of the image
        width = None # Width of one frame
        ):
        if path != None:
            self.images = utility.load_spritesheet(path, width)

        self.delay = delay

        self.timer = 0
        self.frame = 0

    
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
    
    
    def get_frame(self):
        return self.images[self.frame]
    

    def copy(self) -> "Animation":
        obj = Animation(self.delay)
        obj.images = self.images
        return obj
    
    def reset(self):
        self.frame = 0
        self.timer = 0