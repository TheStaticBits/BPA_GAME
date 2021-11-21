import pygame

import src.object_base
import src.constants as constants
import src.animation

class Ellipse(src.object_base.ObjectBase):
    def __init__(self, startPos, velocity = 0):
        super().__init__(__name__)

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.walkingAnim = src.animation.Animation("res/characters/ellipse/walking.png", 16, 10)
        self.idleAnim = src.animation.Animation("res/characters/ellipse/idle.png", 16, 10)

        self.playingAnimation = self.idleAnim

    
    def update(self, room, inputs):
        super().test_grav_line()
        super().update_gravity()

        # Movement here

        super().reset_current_tile()
        super().update_x_collision(room, 0)

        super().update_y_pos()

        super().reset_current_tile()
        super().update_y_collision(room)

        self.playingAnimation.update()
    

    def render(self, window):
        super().render(window)

        self.playingAnimation.render(window, self.rect.x, self.rect.y)