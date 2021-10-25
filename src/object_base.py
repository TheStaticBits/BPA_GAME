import pygame
import math

import src.constants as constants

# ANY OBJECT THAT INHERITS FROM OBJECT_BASE MUST CREATE A RECT OBJECT TO USE TEST_COLLISIONS()

class ObjectBase:
    def __init__(self):
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.yVelocity = 0
    
    def update_gravity(self):
        self.yVelocity -= constants.GRAVITY

    
    def check_tile(self, room, tilePos):
        if room[tilePos[0]][tilePos[1]] == "w":
            tileRect = pygame.Rect(
                tilePos[0] * constants.TILE_SIZE[0], 
                tilePos[1] * constants.TILE_SIZE[1],
                constants.TILE_SIZE[0],
                constants.TILE_SIZE[1]
            )

            if self.rect.colliderect(tempRect):
                return tileRect
    
        return False


    def update_collisions(self, room, dirMoved):
        self.rect.y -= math.ceil(self.yVelocity)
        
        # Resets the self.collisions dictionary
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        # Finds the coordinates of the center of the object
        centerX = self.rect.x + (self.rect.width / 2)
        centerY = self.rect.y + (self.rect.height / 2)

        # Finds the tile that the center of the object is on
        tileX = math.floor(centerX / constants.TILE_SIZE[0])
        tileY = math.floor(centerY / constants.TILE_SIZE[1])

        if dirMoved[0] != 0:
            for y in range(-1, 1):

                tilePos = (tileX + dirMoved[0], tileY + y)
                
                if self.check_tile(room, tilePos):
                    if dirMoved == 1:
                        self.rect.right = tempRect.left
                    else:
                        self.rect.left = tempRect.right
        
        elif dirMoved[1] != 0:
            for x in range(-1, 1):

                tilePos = (tileX + x, tileY + dirMoved[1])

                if self.check_tile(room, tilePos):
                    if dirMoved == 1:
                        self.rect.top = tempRect.bottom
                    else:
                        self.rect.bottom = tempRect.top