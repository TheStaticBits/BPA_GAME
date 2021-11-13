import pygame
from math import floor

import src.constants as constants
import src.utility as utility

# ANY OBJECT THAT INHERITS FROM OBJECT_BASE MUST CREATE A RECT OBJECT TO USE TEST_COLLISIONS()

class ObjectBase:
    def __init__(self):
        # OVERRIDE THIS IN SUBCLASSES
        self.rect = None

        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.yVelocity = 0

        self.currentTile = [0, 0]
        self.spiked = False

        # If this is 1, the gravity is pulling downward
        # If this is -1, the gravity is pulling upward
        self.gravityDir = None

        self.spikeImage = pygame.image.load(constants.SPIKE_PATH).convert_alpha()
        
    
    def reset_current_tile(self):
        # Finds the coordinates of the center of the object
        centerX = self.rect.x + (self.rect.width / 2)
        centerY = self.rect.y + (self.rect.height / 2)

        # Finds the tile that the center of the object is on
        self.currentTile[0] = floor(centerX / constants.TILE_SIZE[0])
        self.currentTile[1] = floor(centerY / constants.TILE_SIZE[1])


    def update_gravity(self):
        self.yVelocity -= constants.GRAVITY * self.gravityDir


    def update_y_pos(self):
        self.rect.y -= round(self.yVelocity)
        
    
    def check_tile(self, room, tilePos):

        offscreen = not utility.check_between(tilePos, (0, 0), constants.SCREEN_TILE_SIZE)

        if offscreen or room[tilePos[1]][tilePos[0]] in constants.TILE_KEYS:
            tileRect = pygame.Rect(
                tilePos[0] * constants.TILE_SIZE[0], 
                tilePos[1] * constants.TILE_SIZE[1],
                constants.TILE_SIZE[0],
                constants.TILE_SIZE[1]
            )

            if self.rect.colliderect(tileRect):
                return tileRect

        elif room[tilePos[1]][tilePos[0]] in constants.SPIKE_ROTATIONS:
            spike = pygame.transform.rotate(
                self.spikeImage, 
                constants.SPIKE_ROTATIONS[room[tilePos[1]][tilePos[0]]]
            )

            spikeMask = pygame.mask.from_surface(spike)
            playerMask = pygame.mask.Mask((self.rect.width, self.rect.height), fill=True)

            collided = spikeMask.overlap(playerMask, (self.rect.x - tilePos[0] * constants.TILE_SIZE[0], self.rect.y - tilePos[1] * constants.TILE_SIZE[1]))

            if collided:
                self.spiked = True
    
        return False


    def update_x_collision(self, room, dirMoved):
        # Resets the self.collisions dictionary
        self.collisions["left"] = False
        self.collisions["right"] = False

        if dirMoved != 0:
            for y in range(-1, 2):
                tilePos = (self.currentTile[0] + dirMoved, self.currentTile[1] + y)
                
                result = self.check_tile(room, tilePos)
                if result != False:
                    if dirMoved == 1:
                        self.rect.right = result.left
                        self.collisions["right"] = True
                    else:
                        self.rect.left = result.right
                        self.collisions["left"] = True
                    
                    break

    
    def update_y_collision(self, room, dirMoved):
        # Resets the self.collisions dictionary
        self.collisions["up"] = False
        self.collisions["down"] = False

        if dirMoved != 0:
            for x in range(-1, 2):
                tilePos = (self.currentTile[0] + x, self.currentTile[1] - dirMoved)

                result = self.check_tile(room, tilePos)
                if result != False:
                    if dirMoved == 1:
                        self.rect.top = result.bottom
                        self.collisions["up"] = True
                    else:
                        self.rect.bottom = result.top
                        self.collisions["down"] = True
                    
                    break
    

    def test_grav_line(self):
        if self.rect.y + (self.rect.height / 2) < (constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]) / 2:
            self.gravityDir = 1 * constants.INVERSE_GRAVITY
            
        else:
            self.gravityDir = -1 * constants.INVERSE_GRAVITY