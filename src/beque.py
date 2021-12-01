import pygame

import src.animation
import src.constants as constants

class Beque:
    def __init__(self):
        self.animation = []
        for name, data in constants.BEQUE_ANIMATIONS.items():
            self.animation[name] = src.animation.Animation(
                data["delay"],
                path = data["path"],
                frames = data["frames"]
            )
        
        
    
    def update(self):
        pass
    
    def render(self):
        pass