import pygame

import src.object_base
import src.constants as constants
import src.animation

class Corlen(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        room, # Room Ellipse is in 
        level, # Level Ellipse is in
        velocity = 0
        ):
        super().__init__(constants.CORLEN_ANIMATIONS, 16)

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = velocity

        self.room = room
        self.level = level

    
    def update(
        self, 
        room, # List of tiles in the current room
        playerPositions
        ):
        if len(playerPositions) > constants.CORLEN_FOLLOW_DISTANCE:
            dirMoved = (playerPositions[0][0] - self.rect.x)
            
            self.rect.x += dirMoved
            self.facing = 1 if dirMoved > 0 else (0 if dirMoved == 0 else -1)

            super().reset_current_tile()
            super().update_x_collision(
                room, 
                self.facing
            )

            self.rect.y += playerPositions[0][1] - self.rect.y

            super().reset_current_tile()
    

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)