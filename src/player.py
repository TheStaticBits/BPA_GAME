import pygame
from math import floor

import src.constants as constants
import src.object_base

class Player(src.object_base.ObjectBase):
    def __init__(self, startPos):
        super().__init__()
        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = 0
    

    def move(self, inputs):
        if inputs["left"]: 
            self.rect.x -= constants.MOVEMENT_SPEED
        
        if inputs["right"]:
            self.rect.x += constants.MOVEMENT_SPEED
        
        
        if self.collisions["down"]:
            if inputs["up"]:
                self.yVelocity = constants.JUMP_FORCE
            else:
                self.yVelocity = 0
        
        if self.collisions["up"]:
            self.yVelocity = 0

        super().move()
            

    def render(self, window):
        pygame.draw.rect(window, (0, 0, 0), self.rect)