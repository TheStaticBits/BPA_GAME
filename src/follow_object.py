import pygame

import src.object_base
import src.animation
import src.utility as utility
import src.constants as constants

class FollowObject(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        room, # Room the object is starting in 
        level, # Level the object is starting in
        followDistance,
        animationList,
        objSize,
        velocity = 0
        ):
        super().__init__(animationList, objSize[0])

        self.followDistance = followDistance
        self.followContinueFrames = 0

        self.room = room
        self.level = level

        self.rect = pygame.Rect(startPos[0], startPos[1], objSize[0], objSize[1])

        self.yVelocity = velocity

    
    def check_below(self, room, globalGrav): # Check if the object is on a platform
        self.yVelocity -= self.gravityDir

        prevY = self.rect.y
        self.update_y_pos()

        result = super().update_y_collision(room, modif=False) # Uses yVelocity and checks if there is a tile below

        self.rect.y = prevY
        self.yVelocity = 0 # Reset yVelocity
        
        return result == True # Return the result

    
    def update(
        self, 
        levels, # List of all levels
        playerPositions,
        playerLevelAndRoom,
        playerFacing,
        playerMoved, # If the player has moved
        globalGravity
        ):
        if len(playerPositions) > self.followDistance: 
            self.level, self.room = playerLevelAndRoom[self.followDistance - self.followContinueFrames] # Setting level and room

            self.facing = playerFacing[self.followDistance - self.followContinueFrames] # Setting facing
            
            if not playerMoved: 
                if self.followContinueFrames < self.followDistance:
                    if self.rect.y != playerPositions[0][1] or not self.check_below(levels[self.level][self.room], globalGravity): # If the entity needs to update its y position (because of gravity) or it isn't on a platform:
                        self.followContinueFrames += 1
                
            else:
                if self.followContinueFrames > 0:
                    if self.rect.y == playerPositions[0][1] or self.check_below(levels[self.level][self.room], globalGravity): # If the entity is not in need of changing
                        self.followContinueFrames -= 1

            self.test_grav_line(globalGravity)
            self.update_animation()

            xMoved = (playerPositions[self.followDistance - self.followContinueFrames][0] - self.rect.x - (constants.PLAYER_WIDTH // 2))
            
            posBeforeMov = self.rect.x
            self.rect.x += xMoved

            super().update_x_collision(
                levels[self.level][self.room], 
                utility.lock_neg1_zero_pos1(xMoved)
            )

            self.rect.y = playerPositions[self.followDistance - self.followContinueFrames][1]

            # Checking both directions after updating y position
            super().update_x_collision(
                levels[self.level][self.room],
                -1
            )

            super().update_x_collision(
                levels[self.level][self.room],
                1
            )

            if self.rect.x != posBeforeMov:
                self.switch_anim("walk")
            
            else:
                self.switch_anim("idle")

            

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)