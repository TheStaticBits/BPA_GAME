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

        tile = room[tilePos[1]][tilePos[0]]

        if offscreen or tile in constants.TILE_KEYS:
            tileRect = pygame.Rect(
                tilePos[0] * constants.TILE_SIZE[0], 
                tilePos[1] * constants.TILE_SIZE[1],
                constants.TILE_SIZE[0],
                constants.TILE_SIZE[1]
            )

            if self.rect.colliderect(tileRect):
                return True, tileRect

        elif tile in constants.SPECIAL_TILES:
            if tile in constants.SPIKE_ROTATIONS:
                image = pygame.transform.rotate(
                    self.spikeImage, 
                    constants.SPIKE_ROTATIONS[tile]
                )
            
            else:
                image = pygame.image.load(constants.SPECIAL_TILE_IMAGE_PATHS[tile]).convert_alpha()

            mask = pygame.mask.from_surface(image)
            playerMask = pygame.mask.Mask((self.rect.width, self.rect.height), fill=True)

            collided = spikeMask.overlap(
                mask, 
                (self.rect.x - tilePos[0] * constants.TILE_SIZE[0], 
                self.rect.y - tilePos[1] * constants.TILE_SIZE[1])
            )

            if collided:
                return False, tile
    
        return False, False


    def update_x_collision(self, room, dirMoved) -> list:
        # Resets the self.collisions dictionary
        self.collisions["left"] = False
        self.collisions["right"] = False

        specialTiles = []

        if dirMoved != 0:
            for y in range(-1, 2):
                for x in range(0, 2):
                    tilePos = (self.currentTile[0] + x * dirMoved, self.currentTile[1] + y)
                    
                    isSolid, result = self.check_tile(room, tilePos)
                    if isSolid:
                        if dirMoved == 1:
                            self.rect.right = result.left
                            self.collisions["right"] = True
                        else:
                            self.rect.left = result.right
                            self.collisions["left"] = True
                        
                        break
                    
                    elif result != False:
                        specialTiles.append(result)
        
        return specialTiles

    
    def update_y_collision(self, room):
        # Resets the self.collisions dictionary
        self.collisions["up"] = False
        self.collisions["down"] = False

        dirMoved = 1 if self.yVelocity > 0 else (0 if self.yVelocity == 0 else -1)

        specialTiles = []

        if dirMoved != 0:
            for y in range(0, 2):
                for x in range(-1, 2):
                    tilePos = (self.currentTile[0] + x, self.currentTile[1] - y * dirMoved)

                    isSolid, result = self.check_tile(room, tilePos)
                    if isSolid:
                        if dirMoved == 1:
                            self.rect.top = result.bottom
                            self.collisions["up"] = True
                        else:
                            self.rect.bottom = result.top
                            self.collisions["down"] = True
                        
                        break
                    
                    elif result != False:
                        specialTiles.append(result)
        
        return specialTiles
    

    def test_grav_line(self):
        if self.rect.y + (self.rect.height / 2) < (constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]) / 2:
            self.gravityDir = 1 * constants.INVERSE_GRAVITY
            
        else:
            self.gravityDir = -1 * constants.INVERSE_GRAVITY