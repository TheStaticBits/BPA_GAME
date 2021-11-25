import pygame

import src.object_base
import src.constants as constants
import src.animation

class Ellipse(src.object_base.ObjectBase):
    def __init__(self, startPos, room, level, velocity = 0):
        super().__init__()

        self.rect = pygame.Rect(32, 32, 16, 16)

        self.walkingAnim = src.animation.Animation(10, "res/characters/ellipse/walking.png", 16)
        self.idleAnim = src.animation.Animation(20, "res/characters/ellipse/idle.png", 16)

        self.playingAnimation = self.idleAnim

        self.yVelocity = velocity

        self.room = room
        self.level = level

    
    def update(self, currentRoom, currentLevel, room):
        if currentRoom == self.room and currentLevel == self.level:
            self.playingAnimation.update()
            self.image = self.playingAnimation.get_frame()

            super().test_grav_line()
            super().update_gravity()

            # Movement here

            super().reset_current_tile()
            super().update_x_collision(room, 0)

            if self.collisions["down"]:
                self.yVelocity = 0

            super().update_y_pos()

            super().reset_current_tile()
            super().update_y_collision(room)
    

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            self.playingAnimation.render(window, (self.rect.x, self.rect.y))