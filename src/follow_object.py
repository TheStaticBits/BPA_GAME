import pygame

import src.object_base
import src.constants as constants
import src.animation

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
        playerMoved, # If the player has moved
        globalGravity
        ):
        if len(playerPositions) > self.followDistance: 
            if not playerMoved: 
                if self.followContinueFrames < self.followDistance:
                    if self.rect.y != playerPositions[0][1] or not self.check_below(levels[self.level][self.room], globalGravity): # If the object needs to update its y position (because of gravity) or it isn't on a platform
                        self.followContinueFrames += 1
                
            else:
                if self.followContinueFrames > 0:
                    self.followContinueFrames -= 2
                
                if self.followContinueFrames < 0:
                    self.followContinueFrames = 0

            self.test_grav_line(globalGravity)
            self.update_animation()

            xMoved = (playerPositions[self.followDistance - self.followContinueFrames][0] - self.rect.x - (constants.PLAYER_WIDTH // 2))
            
            self.rect.x += xMoved

            dirMoved = 1 if xMoved > 0 else (0 if xMoved == 0 else -1)

            if dirMoved != 0:
                self.facing = dirMoved
                self.switch_anim("walk")
            
            else:
                self.switch_anim("idle")

            super().update_x_collision(
                levels[self.level][self.room], 
                dirMoved
            )

            self.level, self.room = playerLevelAndRoom[self.followDistance - self.followContinueFrames] # Setting level and room

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
            

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)