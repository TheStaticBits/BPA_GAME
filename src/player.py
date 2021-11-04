import pygame

import src.constants as constants
import src.object_base

class Player(src.object_base.ObjectBase):
    def __init__(self, startPos):
        super().__init__()

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = 0

        self.canJump = True
    

    def update(self, room, inputs):
        super().update_gravity()

        # This will result in a 0, a 1, or a -1. The inputs are True or False.
        # For example: If both are True, then it will result in 0, meaning no direction moved.
        self.rect.x += (inputs["right"] - inputs["left"]) * constants.MOVEMENT_SPEED
        
        if self.collisions["down"]:
            self.canJump = True
        
        if self.canJump:
            self.canJump = False
            # Inputs is 1 or 0, or True or False
            self.yVelocity = inputs["up"] * constants.JUMP_FORCE

        elif self.collisions["up"]:
            # If the player hit the ceiling
            self.yVelocity = 0

        dirMoved = (
            inputs["right"] - inputs["left"], 
            1 if self.yVelocity > 0 else (0 if self.yVelocity == 0 else -1)
        )
        
        super().update_collisions(room, dirMoved)
            

    def render(self, window):
        pygame.draw.rect(window, (0, 0, 0), self.rect)