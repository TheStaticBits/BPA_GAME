import pygame

import src.object_base
import src.constants as constants
import src.animation

class Corlen(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        room, # Room Corlen is in 
        level, # Level Corlen is in
        velocity = 0
        ):
        super().__init__(constants.CORLEN_ANIMATIONS, 16)

        self.room = room
        self.level = level

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = velocity

        self.followContinueFrames = 0
    

    def check_below(self, room): # Check if Corlen is on a platform
        super().update_gravity() # Adds gravity to yVelocity
        super().update_y_collision(room) # Uses yVelocity and checks if there is a tile below

        ret = self.yVelocity == 0 # Return value
        self.yVelocity = 0 # Reset yVelocity
        
        return ret # Return the return value

    
    def update(
        self, 
        levels, # List of all levels
        playerPositions,
        playerLevelAndRoom,
        playerMoved, # If the player has moved
        globalGravity
        ):
        if len(playerPositions) > constants.CORLEN_FOLLOW_DISTANCE: 
            if not playerMoved: 
                if self.followContinueFrames < constants.CORLEN_FOLLOW_DISTANCE:
                    if self.rect.y != playerPositions[0][1] or not self.check_below(levels[self.level][self.room]): # If Corlen needs to update his y position (because of gravity) or if he isn't on a platform
                        self.followContinueFrames += 1
                
            else:
                if self.followContinueFrames != 0:
                    self.followContinueFrames -= 1

            self.test_grav_line(globalGravity)
            self.update_animation()

            xMoved = (playerPositions[constants.CORLEN_FOLLOW_DISTANCE - self.followContinueFrames][0] - self.rect.x - (constants.PLAYER_WIDTH // 2))
            
            self.rect.x += xMoved

            dirMoved = 1 if xMoved > 0 else (0 if xMoved == 0 else -1)

            if dirMoved != 0:
                self.facing = dirMoved
                self.switch_anim("walk")
            
            else:
                self.switch_anim("idle")

            super().reset_current_tile()
            super().update_x_collision(
                levels[self.level][self.room], 
                dirMoved
            )

            self.level, self.room = playerLevelAndRoom[constants.CORLEN_FOLLOW_DISTANCE - self.followContinueFrames] # Setting level and room

            self.rect.y = playerPositions[constants.CORLEN_FOLLOW_DISTANCE - self.followContinueFrames][1]
            
            

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)
    

    def render_without_room(self, window):
        super().render(window)