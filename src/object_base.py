import pygame
from math import floor

import src.constants as constants
import src.utility as utility

class ObjectBase:
    """
    Base object class.
    Handles collisions through update_x_collision() and update_y_collision().
    Handles animations through switch_anim().
    Allows base classes to access directions in which they collided through the self.collisions dictionary.
    Also handles rendering through the render() function.
    Child classes will have to create their own update() functions.
    """
    def __init__(self, animationData, startPos, size):
        """Initiates rectangles, animations, and other variables"""
        # Used for collisions and keeping track of position
        self.rect = pygame.Rect(startPos[0], startPos[1], size[0], size[1])

        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.yVelocity = 0

        # Tile position that the object's center is on
        self.currentTile = [0, 0]

        # If this is 1, the gravity is pulling downward
        # If this is -1, the gravity is pulling upward
        self.gravityDir = None
        
        self.currentAnim = "idle"
        # Loads all animations into a dictionary
        # With keys being the names of each animation
        self.animations = utility.load_animations_dict(animationData)
        
        # Direction the object is facing (used in rendering)
        # 1 is right, -1 is left
        self.facing = 1
        
    
    def switch_anim(self, newAnim):
        """Changes the animation if it's not already playing the animation given"""
        if self.currentAnim != newAnim:
            self.currentAnim = newAnim
            self.animations[self.currentAnim].reset()
    

    def reset_current_tile(self):
        """Updates the currentTile variable (the tile that the center of the obj is on)"""
        # Finds the coordinates of the center of the object
        centerX = self.rect.x + (self.rect.width / 2)
        centerY = self.rect.y + (self.rect.height / 2)

        # Finds the tile that the center of the object is on
        self.currentTile[0] = floor(centerX / constants.TILE_SIZE[0])
        self.currentTile[1] = floor(centerY / constants.TILE_SIZE[1])


    def update_gravity(self):
        """Adds gravity to the object based on the direction of gravity"""
        self.yVelocity -= constants.GRAVITY * self.gravityDir


    def update_y_pos(self):
        """Update the actual y position with the y velocity"""
        self.rect.y -= round(self.yVelocity)

    
    def update_animation(self):
        """Updates the animation frame"""
        self.animations[self.currentAnim].update()
    

    def get_mask(self) -> "pygame.mask.Mask":
        """Returns the mask of the current frame of the animation of the object"""
        objImage = self.animations[self.currentAnim].get_frame()
        # Flips if the gravity direction is opposite
        objImage = pygame.transform.flip(objImage, False, self.gravityDir == -1)
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
        gravityBeamYPos,
        offset = 0
        ):
        """
        Used in collision testing.
        Checks for collision between a tile and the object.
        Returns a tuple of two elements.
        First, whether it was a collision between a solid tile,
        and then the tile rectangle if it was solid, the tile character if it wasn't solid, and False otherwise.
        """

        # Testing if the y or x positions of the given tile are on the screen
        yPosOnScreen = 0 <= tilePos[1] < constants.SCREEN_TILE_SIZE[1]
        xPosOnScreen = 0 <= tilePos[0] < constants.SCREEN_TILE_SIZE[0]
        
        tileOnScreen = xPosOnScreen and yPosOnScreen

        # If the y position is offscreen but the x position is on screen
        makeYTileCheck = not yPosOnScreen and xPosOnScreen

        # If the tile is off the level (not just the room), make a tile and check for collisions
        makeXTileCheck = tilePos[0] < 0 and roomNumber == 0 or tilePos[0] >= constants.SCREEN_TILE_SIZE[0] and roomNumber == len(level) - 1

        if makeYTileCheck or makeXTileCheck or tileOnScreen and room[tilePos[1]][tilePos[0]] in constants.TILE_KEYS:
            # Creates a rectangle at the tile position
            tileRect = pygame.Rect(
                tilePos[0] * constants.TILE_SIZE[0] + offset, 
                tilePos[1] * constants.TILE_SIZE[1],
                constants.TILE_SIZE[0],
                constants.TILE_SIZE[1]
            )

            if self.rect.colliderect(tileRect):
                return True, tileRect

        # If the tile is on screen, and the tile is a special tile    
        elif tileOnScreen and room[tilePos[1]][tilePos[0]] in constants.SPECIAL_TILES:
            if tileRenderer is not None:
                tile = room[tilePos[1]][tilePos[0]] # tile character (such as "w")

                if tile in constants.SPIKE_ROTATIONS: # If it's a spike
                    # Rotates the spike image and sets it as the image
                    image = pygame.transform.rotate(
                        pygame.image.load(constants.SPIKE_PATH).convert_alpha(), 
                        constants.SPIKE_ROTATIONS[tile]
                    )
                
                else:
                    # Gets the tile's animation frame from the tile renderer
                    image = tileRenderer.get_tile_anim_frame(tilePos,  globalGravity, gravityBeamYPos)
                
                tileMask = pygame.mask.from_surface(image)
                objMask = self.get_mask()

                # Checking pixel perfect mask collisions
                collided = tileMask.overlap(
                    objMask, 
                    (self.rect.x - tilePos[0] * constants.TILE_SIZE[0] - offset, 
                    self.rect.y - tilePos[1] * constants.TILE_SIZE[1])
                )

                if collided:
                    return False, tile
        
        # If the y position is on screen, the x position isn't, then 
        # test the tile in the other room
        elif not xPosOnScreen and yPosOnScreen: 
            if tilePos[0] < 0:
                roomNum = roomNumber - 1
                tileX = tilePos[0] + constants.SCREEN_TILE_SIZE[0] # Flips it to the other side of the screen
                offs = -constants.SCREEN_SIZE[0] # Offset for collision testing

            # Same as above, just in reverse for the other direction
            elif tilePos[0] >= constants.SCREEN_TILE_SIZE[0]:
                roomNum = roomNumber + 1
                tileX = tilePos[0] - constants.SCREEN_TILE_SIZE[0]
                offs = constants.SCREEN_SIZE[0]
            
            # If the checking room number is not off the level
            if 0 <= roomNum < len(level):
                # Use the same function we're in right now to check the tile!
                return self.check_tile(
                    level[roomNum],
                    roomNum, 
                    level, 
                    (tileX, tilePos[1]),
                    tileRenderer,
                    globalGravity,
                    gravityBeamYPos,
                    offset = offs
                )

        return False, False


    def update_x_collision(
        self, 
        room, 
        roomNum, 
        level, 
        dirMoved, # 1, 0, or -1 for the direction moved so it can check in only that direction
        tileRenderer = None, 
        globalGravity = None, 
        gravityBeamYPos = None
        ) -> dict: # Returns any special tiles and their positions the object collided with
        """
        Checks for tiles around the object based on the direction moved.
        """
        self.reset_current_tile()

        # Resets the self.collisions dictionary
        self.collisions["left"] = False
        self.collisions["right"] = False

        specialTiles = {} # any special tiles touched

        if dirMoved != 0: # If the object hasn't gone no direction at all
            # Checks tiles to the left/right of the object's center tile (based on direction moved)
            # For example, if the object moved LEFT:
            # Key: O is object, X are tiles being checked, and . are tiles not being checked
            # . . . . . .
            # . . . X X .
            # . . . X O .
            # . . . X X .
            # . . . . . .
            # (also checks the tile that the player is on)
            # This is also the same for moving right

            for y in range(-1, 2):
                for x in range(0, 2):
                    # Tile position of tile being checked
                    tilePos = (self.currentTile[0] + x * dirMoved, self.currentTile[1] + y)
                    
                    isSolid, result = self.check_tile(room, roomNum, level, tilePos, tileRenderer, globalGravity, gravityBeamYPos)
                        
                    if isSolid: # If the tile being checked was a solid rectangle
                        if dirMoved == 1: # Moved right
                            # Sets the right side of the object to the left side of the tile
                            self.rect.right = result.left 
                            self.collisions["right"] = True
                        else: # Moved left
                            self.rect.left = result.right
                            self.collisions["left"] = True
                        
                        return specialTiles # Exits
                    
                    elif result is not False:
                        specialTiles[result] = tilePos
        
        return specialTiles

    
    def update_y_collision(
        self, 
        room, 
        roomNum, 
        level, 
        tileRenderer = None, 
        globalGravity = None, 
        gravityBeamYPos = None, 
        modif = True
        ) -> dict: # Also returns a dictionary of special tiles touched and their positions
        """Checks the tiles in the direction the object has moved (bases on the y velocity)"""
        self.reset_current_tile()

        # Resets the self.collisions dictionary
        self.collisions["up"] = False
        self.collisions["down"] = False

        # Locks to 1, 0, or -1
        dirMoved = utility.lock_neg1_zero_pos1(self.yVelocity)

        specialTiles = {}

        if dirMoved != 0:
            # Same system as checking x positions
            # just rotated for up/down instead of left/right
            for y in range(0, 2):
                for x in range(-1, 2):
                    # Position of tile being checked
                    tilePos = (self.currentTile[0] + x, self.currentTile[1] - y * dirMoved)

                    isSolid, result = self.check_tile(room, roomNum, level, tilePos, tileRenderer, globalGravity, gravityBeamYPos)
                    if isSolid:
                        if modif: # If it wants it to move the object based on what it found
                            if dirMoved == 1:
                                self.rect.top = result.bottom
                                self.collisions["up"] = True
                            else:
                                self.rect.bottom = result.top
                                self.collisions["down"] = True
                            
                            return specialTiles # Ending collision testing
                    
                        else: # If modif was explicitly set to be false
                            if result is not False:
                                return True
                    
                    elif result is not False:
                        specialTiles[result] = tilePos
        
        return specialTiles
    

    def test_grav_line(self, globalGravity, gravBeamYPos):
        """Tests the gravity line, changing the gravity direction based on the result"""
        # globalGravity, if -1, switches the gravity beam pull direction
        # (this is for functionality of the gravity orb)

        # Checks the center of the object against the gravity beam's y position
        if self.rect.y + (self.rect.height / 2) < (gravBeamYPos * constants.TILE_SIZE[1]):
            self.gravityDir = 1 * globalGravity
            
        else:
            self.gravityDir = -1 * globalGravity
    

    def render(self, window, offset = 0):
        """Renders to the screen, with a given offset (if provided one)"""
        frame = self.animations[self.currentAnim].get_frame()

        # Flips the image horizontally if the facing is the opposite direction
        # Flips the image vertically if the gravity direction is negative
        frame = pygame.transform.flip(frame, self.facing == -1, self.gravityDir == -1)

        window.blit(frame, (self.rect.x + offset, self.rect.y))