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


    def move(self):
        self.yVelocity -= constants.GRAVITY
        self.rect.y -= self.yVelocity

    
    def test_collisions(self, room):
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

        # Check the collision of the object with the tile above the object using pygame.Rect.colliderect
        if room[tileY - 1][tileX] == "w":
            tempRect = pygame.Rect(tileX * constants.TILE_SIZE[0], (tileY - 1) * constants.TILE_SIZE[1], constants.TILE_SIZE[0], constants.TILE_SIZE[1])

            if self.rect.colliderect(tempRect):
                self.rect.top = tempRect.bottom
                self.collisions["up"] = True
        
        # Check the collision of the object with the tile below the object using pygame.Rect.colliderect
        if room[tileY + 1][tileX] == "w":
            tempRect = pygame.Rect(tileX * constants.TILE_SIZE[0], (tileY + 1) * constants.TILE_SIZE[1], constants.TILE_SIZE[0], constants.TILE_SIZE[1])

            if self.rect.colliderect(tempRect):
                self.rect.bottom = tempRect.top
                self.collisions["down"] = True

        # Check the collision of the object with the tile to the left of the object using pygame.Rect.colliderect
        if room[tileY][tileX - 1] == "w":
            tempRect = pygame.Rect((tileX - 1) * constants.TILE_SIZE[0], tileY * constants.TILE_SIZE[1], constants.TILE_SIZE[0], constants.TILE_SIZE[1])

            if self.rect.colliderect(tempRect):
                self.rect.left = tempRect.right
                self.collisions["left"] = True
        
        # Check the collision of the object with the tile to the right of the object using pygame.Rect.colliderect
        if room[tileY][tileX + 1] == "w":
            tempRect = pygame.Rect((tileX + 1) * constants.TILE_SIZE[0], tileY * constants.TILE_SIZE[1], constants.TILE_SIZE[0], constants.TILE_SIZE[1])

            if self.rect.colliderect(tempRect):
                self.rect.right = tempRect.left
                self.collisions["right"] = True