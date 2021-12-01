import pygame
from math import floor

import src.constants as constants
import src.utility as utility
import src.animation

# ANY OBJECT THAT INHERITS FROM OBJECT_BASE MUST CREATE A RECT OBJECT TO USE TEST_COLLISIONS()

class ObjectBase:
    def __init__(self, animationData, width):

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

        # If this is 1, the gravity is pulling downward
        # If this is -1, the gravity is pulling upward
        self.gravityDir = None

        self.cachedMasks = {}
        
        self.currentAnim = "idle"
        self.animations = {}
        for name, data in animationData.items():
            self.animations[name] = src.animation.Animation(
                data["delay"],
                path = data["path"],
                width = width
            )
        
        self.facing = 1
        
    
    def switch_anim(self, newAnim):
        if self.currentAnim != newAnim:
            self.currentAnim = newAnim
            self.animations[self.currentAnim].reset()
    

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

    
    def update_animation(self):
        self.animations[self.currentAnim].update()
        
    
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
                return True, tileRect

        elif not offscreen and room[tilePos[1]][tilePos[0]] in constants.SPECIAL_TILES:
            tile = room[tilePos[1]][tilePos[0]]

            if not (tile in self.cachedMasks):
                if tile in constants.SPIKE_ROTATIONS: # If it's a spike
                    image = pygame.transform.rotate(
                        pygame.image.load(constants.SPIKE_PATH).convert_alpha(), 
                        constants.SPIKE_ROTATIONS[tile]
                    )
                
                else:
                    image = pygame.image.load(constants.TILES_WITH_ANIMATIONS[tile]["mask"]).convert()
                    image.set_colorkey((255, 255, 255))
                
                objMask = pygame.mask.from_surface(image)
                self.cachedMasks[tile] = objMask

            playerImage = pygame.transform.flip(self.animations[self.currentAnim].get_frame(), False, self.gravityDir == -1) # self.images REQUIRED FOR CHILD CLASSES
            playerMask = pygame.mask.from_surface(playerImage)

            collided = self.cachedMasks[tile].overlap(
                playerMask, 
                (self.rect.x - tilePos[0] * constants.TILE_SIZE[0], 
                self.rect.y - tilePos[1] * constants.TILE_SIZE[1])
            )

            if collided:
                return False, tile
    
        return False, False


    def update_x_collision(self, room, dirMoved) -> dict:
        self.reset_current_tile()

        # Resets the self.collisions dictionary
        self.collisions["left"] = False
        self.collisions["right"] = False

        specialTiles = {}

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
                        specialTiles[result] = tilePos
        
        return specialTiles

    
    def update_y_collision(self, room, modif=True) -> dict:
        self.reset_current_tile()

        # Resets the self.collisions dictionary
        self.collisions["up"] = False
        self.collisions["down"] = False

        dirMoved = utility.lock_neg1_zero_pos1(self.yVelocity)

        specialTiles = {}

        if dirMoved != 0:
            for y in range(0, 2):
                for x in range(-1, 2):
                    tilePos = (self.currentTile[0] + x, self.currentTile[1] - y * dirMoved)

                    isSolid, result = self.check_tile(room, tilePos)
                    if isSolid:
                        if modif:
                            if dirMoved == 1:
                                self.rect.top = result.bottom
                                self.collisions["up"] = True
                            else:
                                self.rect.bottom = result.top
                                self.collisions["down"] = True
                            
                            break
                    
                        else:
                            if result != False:
                                return True
                    
                    elif result != False:
                        specialTiles[result] = tilePos
        
        return specialTiles
    

    def test_grav_line(self, globalGravity):
        if self.rect.y + (self.rect.height / 2) < (constants.GRAV_BEAM_TILE_Y_POS * constants.TILE_SIZE[1]):
            self.gravityDir = 1 * globalGravity
            
        else:
            self.gravityDir = -1 * globalGravity
    

    def render(self, window):
        frame = self.animations[self.currentAnim].get_frame()

        frame = pygame.transform.flip(frame, self.facing == -1, self.gravityDir == -1)

        window.blit(frame, (self.rect.x, self.rect.y))