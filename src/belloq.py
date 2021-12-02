import pygame
import math

import src.animation
import src.constants as constants

class Lazer:
    def __init__(
        self, 
        degreesFacing, # What direction it's facing in radians 
        startPos 
        ):
        self.degreesFacing = degreesFacing
        self.position = startPos
    

    def update(self, playerMask, playerPos):
        self.position[0] += math.cos(self.degreesFacing) * constants.LAZER_SPEED
        self.position[1] += math.sin(self.degreesFacing) * constants.LAZER_SPEED

        self.endPoint = (
            self.position[0] + (math.cos(self.degreesFacing) * constants.LAZER_LENGTH),
            self.position[1] + (math.sin(self.degreesFacing) * constants.LAZER_LENGTH)
        )

        collisionSurface = pygame.Surface((
            self.endPoint[0] - self.position[0],
            self.endPoint[1] - self.position[1]
        ))

        pygame.draw.line(
            collisionSurface, 
            constants.LAZER_COLOR,
            self.position,
            self.endPoint
        )

        lineMask = pygame.mask.from_surface(collisionSurface)

        collCheck = lineMask.overlap(
            playerMask,
            # Gets the lessor of the two and then subtracts the player's position to find the offset
            (self.position[0] if self.position[0] < self.endPoint[0] else self.endPoint[0]) - playerPos[0],
            (self.position[1] if self.position[1] < self.endPoint[1] else self.endPoint[1]) - playerPos[1]
        )

        return collCheck

    
    def render(self, window):
        pygame.draw.line(
            window, 
            constants.LAZER_COLOR,
            self.position,
            self.endPoint
        )


class Belloq:
    def __init__(self):
        self.animation = []
        for name, data in constants.BEQUE_ANIMATIONS.items():
            self.animation[name] = src.animation.Animation(
                data["delay"],
                path = data["path"],
                frames = data["frames"]
            )
        self.currentAnim = ""

        self.position = [0, 0]
        
    
    def switchAnim(self, newAnim):
        if newAnim != self.currentAnim:
            self.currentAnim = newAnim
            self.animation[self.currentAnim].reset()

    
    def update(self, player):
        self.animation[self.currentAnim].update()

    
    def render(self, window):
        self.animation[self.currentAnim].render(window, self.position)