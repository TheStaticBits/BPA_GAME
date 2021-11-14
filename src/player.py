import pygame

import src.constants as constants
import src.object_base

class Player(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        velocity = 0
        ):
        super().__init__()

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = velocity

        self.canJump = True
    

    def update(self, room, inputs) -> str:
        super().test_grav_line()
        super().update_gravity()

        # This will result in a 0, a 1, or a -1. The inputs are True or False.
        # For example: If both are True, then it will result in 0, meaning no direction moved.
        self.rect.x += (inputs["right"] - inputs["left"]) * constants.MOVEMENT_SPEED

        super().reset_current_tile()
        super().update_x_collision(room, inputs["right"] - inputs["left"])

        if self.collisions["right"]:
            if self.rect.x / constants.TILE_SIZE[0] == constants.SCREEN_TILE_SIZE[0] - 1:
                return "right"
        
        elif self.collisions["left"]:
            if self.rect.x == 0:
                return "left"
        
        # Update velocity based on inputs
        if (self.gravityDir == 1 and self.collisions["down"]) or (self.gravityDir == -1 and self.collisions["up"]):
            self.canJump = True
            self.yVelocity = 0
        
        if inputs["up"] and self.canJump:
            self.canJump = False
            # Inputs is 1 or 0, or True or False
            self.yVelocity = constants.JUMP_FORCE * self.gravityDir

        # If the player hit the ceiling reset y velocity
        elif (self.gravityDir == 1 and self.collisions["up"]) or (self.gravityDir == -1 and self.collisions["down"]):
            if (self.gravityDir == 1 and self.yVelocity > 0) or (self.gravityDir == -1 and self.yVelocity < 0):
                self.yVelocity = 0
        
        if (self.gravityDir == 1 and round(self.yVelocity < -1)) or (self.gravityDir == -1 and round(self.yVelocity > 1)):
            self.canJump = False

        super().update_y_pos()
        
        super().reset_current_tile()
        super().update_y_collision(room, 1 if self.yVelocity > 0 else (0 if self.yVelocity == 0 else -1))

        if self.spiked:
            return "dead"
        
        return "alive"
        

    def render(self, window):
        pygame.draw.rect(window, (0, 0, 0), self.rect)