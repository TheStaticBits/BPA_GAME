import pygame

import src.constants as constants
import src.object_base
import src.animation

class Player(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        yVelocity = 0,
        xVelocity = 0
        ):
        super().__init__(constants.PLAYER_ANIMATIONS, constants.PLAYER_WIDTH)
        
        # Used for collisions and keeping track of position
        self.rect = pygame.Rect(startPos[0], startPos[1], constants.PLAYER_WIDTH, constants.TILE_SIZE[1])

        self.yVelocity = yVelocity
        self.xVelocity = xVelocity

        self.canJump = True

        self.dirMoved = 0
    

    def reset(self, pos, yVelocity, xVelocity):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.yVelocity = yVelocity
        self.xVelocity = xVelocity
    

    def update(
        self, 
        room, # List of tiles in the current room
        inputs, # Input dictionary
        globalGravity = None, # The gravity of the world
        ) -> str:

        super().update_animation()

        if not (globalGravity is None):
            super().test_grav_line(globalGravity)
        else:
            self.gravityDir = 1 # Setting it to normal gravity
        
        super().update_gravity()

        # This will result in a 0, a 1, or a -1. The inputs are True or False.
        # For example: If both are True, then it will result in 0, meaning no direction moved.
        self.dirMoved = inputs["right"] - inputs["left"]

        # If the player moved
        if self.dirMoved != 0:
            self.xVelocity += self.dirMoved * constants.SPEED_UP_SPEED

            # Clamping the xVelocity to the max speed in both directions (negative and positive)
            self.xVelocity = max(self.xVelocity, -constants.MAX_SPEED)
            self.xVelocity = min(self.xVelocity, constants.MAX_SPEED)

            if self.collisions["left"] or self.collisions["right"]: # If the player hit a wall, left or right
                self.xVelocity = 0

        else: # If the player did not move
            if round(self.xVelocity) != 0:
                # Moves the xVelocity towards 0
                self.xVelocity += (self.xVelocity < 0) * constants.SPEED_UP_SPEED + (self.xVelocity > 0) * -constants.SPEED_UP_SPEED

            else:
                self.xVelocity = 0
        
        # Applying the xVelocity to the player's position
        self.rect.x += round(self.xVelocity)

        super().reset_current_tile()
        specialTiles = super().update_x_collision(
            room, 
            1 if self.xVelocity > 0 else (0 if self.xVelocity == 0 else -1)
        )

        if self.dirMoved != 0:
            self.switch_anim("walk")

        else:
            self.switch_anim("idle")

        
        # Update velocity based on inputs
        if (self.gravityDir == 1 and self.collisions["down"]) or (self.gravityDir == -1 and self.collisions["up"]):
            self.canJump = True
            self.yVelocity = 0
        
        if inputs["up"] and self.canJump:
            self.canJump = False
            # Inputs is 1 or 0, or True or False
            self.yVelocity = constants.JUMP_FORCE * self.gravityDir

        # If the player hit the ceiling reset y velocity
        elif (self.gravityDir == 1 and self.collisions["up"]) or (self.gravityDir == -1 and self.collisions["down"]):
            if (self.gravityDir == 1 and self.yVelocity > 0) or (self.gravityDir == -1 and self.yVelocity < 0):
                self.yVelocity = 0
        
        if (self.gravityDir == 1 and round(self.yVelocity < -1)) or (self.gravityDir == -1 and round(self.yVelocity > 1)):
            self.canJump = False

        super().update_y_pos()
        
        super().reset_current_tile()

        result = super().update_y_collision(room)
        for tile, tilePos in result.items():
            specialTiles[tile] = tilePos

        # Handle special tiles
        for tile, position in specialTiles.items():
            if tile == "j":
                if inputs["up"]:
                    self.yVelocity = constants.JUMP_FORCE * self.gravityDir
                    return (tile, position)
                
            elif tile == "c" or tile == "g":
                return (tile, position)
            
            elif tile in constants.SPIKE_ROTATIONS:
                return "dead"
            
            else:
                if inputs["up"]:
                    return (tile, position)


        if self.collisions["right"]:
            if self.rect.x == constants.TILE_SIZE[0] * constants.SCREEN_TILE_SIZE[0] - constants.PLAYER_WIDTH:
                return "right"
        
        elif self.collisions["left"]:
            if self.rect.x == 0:
                return "left"

        return "alive"