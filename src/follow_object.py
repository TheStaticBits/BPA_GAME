import pygame

import src.object_base
import src.animation
import src.utility as utility
import src.constants as constants

"""
Handles an object which follows the player (such as Ellipse and Corlen ingame)
Inherits from ObjectBase to get collision testing functionality
"""
class FollowObject(src.object_base.ObjectBase):
    # Sets up variables and parent class
    def __init__(
        self, 
        startPos, 
        room, # Room the object is starting in 
        level, # Level the object is starting in
        followDistance, # Distance in frames at which the object follows from
        animationList,
        objSize,
        velocity = 0
        ):
        super().__init__(animationList, startPos, objSize)

        self.followDistance = followDistance
        self.followContinueFrames = 0

        self.room = room
        self.level = level

        self.yVelocity = velocity


    # Check if the object is on a platform
    def check_below(self, level): 
        self.yVelocity -= self.gravityDir
        
        self.update_y_pos() # Changes y position based on yVelocity

        # Uses yVelocity and checks if there is a tile below without moving the object
        result = super().update_y_collision(level[self.room], self.room, level, modif = False) 
        
        self.yVelocity = 0 # Reset yVelocity
        
        return result is True # If there was a collision below the object

    
    # Moves the follow object, updating animation and everything else
    def update(
        self, 
        levels, # List of all levels
        playerPositions,
        playerLevelAndRoom,
        playerFacing,
        playerMoved, # If the player has moved
        gravBeamYPos,
        globalGravity
        ):
        super().test_grav_line(globalGravity, gravBeamYPos) # Updates the gravity direction
        super().update_animation()

        if len(playerPositions) > self.followDistance: # If the player has moved far enough for the object to start following 
            self.level, self.room = playerLevelAndRoom[self.followDistance] # Setting level and room

            self.facing = playerFacing[self.followDistance - self.followContinueFrames] # Setting facing
            
            if not playerMoved: # If the player hasn't moved
                # self.followDistance is a variable which describes how far 
                # forward the object is in frames from where it was before the player
                # stopped moving
                # it only moves forward if the object in question is in an illegal state
                # such as floating in midair
                # So that the object continues moving while the player is still so it doesn't
                # stay floating in the air, for example. 

                if self.followContinueFrames < self.followDistance:
                    # If the entity needs to update its y position (because of gravity) or it isn't on a platform
                    if self.rect.y != playerPositions[0][1] or not self.check_below(levels[self.level]):
                        self.followContinueFrames += 1
                
            else: # Player has moved
                if self.followContinueFrames > 0:
                    if self.rect.y == playerPositions[0][1] or self.check_below(levels[self.level]): # If the entity is not in need of changing
                        self.followContinueFrames -= 1

            # Distance the object moved
            xMoved = (
                playerPositions[self.followDistance - self.followContinueFrames][0] # player x position
                 - self.rect.x - (constants.PLAYER_WIDTH // 2)
            )
            
            posBeforeMove = self.rect.x
            self.rect.x += xMoved

            super().update_x_collision(
                levels[self.level][self.room],
                self.room,
                levels[self.level], 
                utility.lock_neg1_zero_pos1(xMoved)
            )

            self.rect.y = playerPositions[self.followDistance - self.followContinueFrames][1]

            # Checking both directions after updating y position
            super().update_x_collision(
                levels[self.level][self.room],
                self.room,
                levels[self.level],
                -1 # Checking to the left
            )

            super().update_x_collision(
                levels[self.level][self.room],
                self.room,
                levels[self.level],
                1 # Checking to the right
            )

            # Setting animation
            if self.rect.x != posBeforeMove:
                self.switch_anim("walk")
            
            else:
                self.switch_anim("idle")

    # Render the object without a check for room and level
    # Used for boss levels
    def render_move_over(self, surface, playerRoomNum, offset = 0):
        if playerRoomNum != self.room:
            # Finds the room offset
            dir = 1 if playerRoomNum - self.room == -1 else -1
            # Rendering it along with a room offset
            super().render(surface, offset = offset + (dir * constants.SCREEN_SIZE[0]))
        
        else:
            # Rendering normally
            super().render(surface, offset = offset)


    # Renders the object only if the room and level passed in are
    # the same as the ones of this object
    def render_with_check(self, currentRoom, currentLevel, window, offset = 0):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window, offset = offset)