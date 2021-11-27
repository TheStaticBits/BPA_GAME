import pygame

import src.object_base
import src.constants as constants
import src.animation

class Ellipse(src.object_base.ObjectBase):
    def __init__(self, startPos, room, level, velocity = 0):
        super().__init__(constants.ELLIPSE_ANIMATIONS, 16)
        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = velocity

        self.room = room
        self.level = level

        self.facing = 1

    
    def update(
        self, 
        currentRoom, # Current room number 
        currentLevel, # Current level number
        room, # List of tiles in the current room
        globalGravity
        ):

        if currentRoom == self.room and currentLevel == self.level:
            super().test_grav_line(globalGravity)
            super().update_gravity()

            super().reset_current_tile()
            super().update_x_collision(room, 0)

            if self.collisions["down"] or self.collisions["up"]:
                self.yVelocity = 0

            super().update_y_pos()

            super().reset_current_tile()
            super().update_y_collision(room)
    

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)