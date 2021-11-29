import pygame

import src.object_base
import src.constants as constants
import src.animation

class Ellipse(src.object_base.ObjectBase):
    def __init__(
        self, 
        startPos, 
        room, # Room Ellipse is in 
        level, # Level Ellipse is in
        velocity = 0
        ):
        super().__init__(constants.ELLIPSE_ANIMATIONS, 16)

        self.room = room
        self.level = level

        self.rect = pygame.Rect(startPos[0], startPos[1], 16, 16)

        self.yVelocity = velocity

        self.followContinueFrames = 0

    
    def update(
        self, 
        room, # List of tiles in the current room
        playerPositions,
        globalGravity
        ):
        if len(playerPositions) > constants.ELLIPSE_FOLLOW_DISTANCE: 
            if playerPositions[constants.ELLIPSE_FOLLOW_DISTANCE - self.followContinueFrames] == (self.rect.x, self.rect.y): # If the position the player moved to and the position of Ellipse are the same, meaning the player hasn't moved
                if self.followContinueFrames != constants.ELLIPSE_FOLLOW_DISTANCE:
                    if playerPositions[constants.ELLIPSE_FOLLOW_DISTANCE - self.followContinueFrames - 1][1] != self.rect.y: # If Ellipse needs to update its y position (because of gravity)
                        print("stage 3")
                        self.followContinueFrames += 1
                
            else:
                if self.followContinueFrames != 0:
                    self.followContinueFrames -= 1

            self.test_grav_line(globalGravity)
            self.update_animation()

            xMoved = (playerPositions[constants.ELLIPSE_FOLLOW_DISTANCE - self.followContinueFrames][0] - self.rect.x)
            
            self.rect.x += xMoved

            dirMoved = 1 if xMoved > 0 else (0 if xMoved == 0 else -1)

            if dirMoved != 0:
                self.facing = dirMoved

            if self.facing == 0:
                self.switch_anim("idle")
            
            else:
                self.switch_anim("walk")

            super().reset_current_tile()
            super().update_x_collision(
                room, 
                dirMoved
            )

            self.rect.y += playerPositions[constants.ELLIPSE_FOLLOW_DISTANCE - self.followContinueFrames][1] - self.rect.y

            super().reset_current_tile()
            

    def render(self, currentRoom, currentLevel, window):
        if currentRoom == self.room and currentLevel == self.level:
            super().render(window)
    

    def render_without_room(self, window):
        super().render(window)