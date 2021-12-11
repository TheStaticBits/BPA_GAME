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
    

    def get_mask(self):
        objImage = pygame.transform.flip(self.animations[self.currentAnim].get_frame(), False, self.gravityDir == -1)
        objMask = pygame.mask.from_surface(objImage)

        return objMask
        
    
    def check_tile(
        self, 
        room, 
        roomNumber, 
        level, 
        tilePos, 
        tileRenderer,
        globalGravity,
        offset = 0
        ):

        yPosOnScreen = 0 <= tilePos[1] < constants.SCREEN_TILE_SIZE[1]
        xPosOnScreen = 0 <= tilePos[0] < constants.SCREEN_TILE_SIZE[0]
        tileOnScreen = xPosOnScreen and yPosOnScreen

        makeYTileCheck = not yPosOnScreen and xPosOnScreen

        # If the tile is off the level, make a tile and check for collisions
        makeXTileCheck = tilePos[0] < 0 and roomNumber == 0 or tilePos[0] >= constants.SCREEN_TILE_SIZE[0] and roomNumber == len(level) - 1

        if makeYTileCheck or makeXTileCheck or tileOnScreen and room[tilePos[1]][tilePos[0]] in constants.TILE_KEYS:
            tileRect = pygame.Rect(
                tilePos[0] * constants.TILE_SIZE[0] + offset, 
                tilePos[1] * constants.TILE_SIZE[1],
                constants.TILE_SIZE[0],
                constants.TILE_SIZE[1]
            )

            if self.rect.colliderect(tileRect):
                return True, tileRect

        elif tileOnScreen and room[tilePos[1]][tilePos[0]] in constants.SPECIAL_TILES:
            tile = room[tilePos[1]][tilePos[0]]

            if tileRenderer is not None:
                if tile in constants.SPIKE_ROTATIONS: # If it's a spike
                    image = pygame.transform.rotate(
                        pygame.image.load(constants.SPIKE_PATH).convert_alpha(), 
                        constants.SPIKE_ROTATIONS[tile]
                    )
                
                else:
                    image = tileRenderer.get_tile_anim_frame(tilePos, globalGravity)
                
                tileMask = pygame.mask.from_surface(image)
                objMask = self.get_mask()

                collided = tileMask.overlap(
                    objMask, 
                    (self.rect.x - tilePos[0] * constants.TILE_SIZE[0] - offset, 
                    self.rect.y - tilePos[1] * constants.TILE_SIZE[1])
                )

                if collided:
                    return False, tile
            
        elif not xPosOnScreen and yPosOnScreen: # If the y position is on screen, the x position isn't, test the tile in the other room
            if tilePos[0] < 0:
                roomNum = roomNumber - 1
                tileX = tilePos[0] + constants.SCREEN_TILE_SIZE[0]
                offs = -constants.SCREEN_SIZE[0]

            elif tilePos[0] >= constants.SCREEN_TILE_SIZE[0]:
                roomNum = roomNumber + 1
                tileX = tilePos[0] - constants.SCREEN_TILE_SIZE[0]
                offs = constants.SCREEN_SIZE[0]
            
            if 0 <= roomNum < len(level):
                return self.check_tile(
                    level[roomNum],
                    roomNum, 
                    level, 
                    (tileX, tilePos[1]),
                    tileRenderer,
                    globalGravity,
                    offset = offs
                )
    
        return False, False


    def update_x_collision(self, room, roomNum, level, dirMoved, tileRenderer = None, globalGravity = None) -> dict:
        self.reset_current_tile()

        # Resets the self.collisions dictionary
        self.collisions["left"] = False
        self.collisions["right"] = False

        specialTiles = {}

        if dirMoved != 0:
            for y in range(-1, 2):
                for x in range(0, 2):
                    tilePos = (self.currentTile[0] + x * dirMoved, self.currentTile[1] + y)
                    
                    isSolid, result = self.check_tile(room, roomNum, level, tilePos, tileRenderer, globalGravity)
                        
                    if isSolid:
                        if dirMoved == 1:
                            self.rect.right = result.left
                            self.collisions["right"] = True
                        else:
                            self.rect.left = result.right
                            self.collisions["left"] = True
                        
                        break
                    
                    elif result is not False:
                        specialTiles[result] = tilePos
        
        return specialTiles

    
    def update_y_collision(self, room, roomNum, level, tileRenderer = None, globalGravity = None, modif=True) -> dict:
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

                    isSolid, result = self.check_tile(room, roomNum, level, tilePos, tileRenderer, globalGravity)
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
                            if result is not False:
                                return True
                    
                    elif result is not False:
                        specialTiles[result] = tilePos
        
        return specialTiles
    

    def test_grav_line(self, globalGravity, gravBeamYPos):
        if self.rect.y + (self.rect.height / 2) < (gravBeamYPos * constants.TILE_SIZE[1]):
            self.gravityDir = 1 * globalGravity
            
        else:
            self.gravityDir = -1 * globalGravity
    

    def render(self, window, offset = 0):
        frame = self.animations[self.currentAnim].get_frame()

        frame = pygame.transform.flip(frame, self.facing == -1, self.gravityDir == -1)

        window.blit(frame, (self.rect.x + offset, self.rect.y))