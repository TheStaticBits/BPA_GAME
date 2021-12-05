import pygame
import random
import math

import src.animation
import src.constants as constants

class Lazer:
    def __init__(
        self, 
        degreesFacing, # What direction it's facing in radians 
        startPos 
        ):
        self.degreesFacing = degreesFacing
        self.position = list(startPos)
    
    
    def get_top_left(self):
        # Gets the lessor of the two points, for the top left
        topLeftX = self.position[0] if self.position[0] < self.endPoint[0] else self.endPoint[0]
        topLeftY = self.position[1] if self.position[1] < self.endPoint[1] else self.endPoint[1]
        return (topLeftX, topLeftY)
    

    def get_bottom_right(self):
        # Gets the greater of the two points, for the bottom right
        bottomRightX = self.position[0] if self.position[0] > self.endPoint[0] else self.endPoint[0]
        bottomRightY = self.position[1] if self.position[1] > self.endPoint[1] else self.endPoint[1]
        return(bottomRightX, bottomRightY)
    

    def update(self, playerMask, playerPos, tilesOffset):
        self.position[0] += math.cos(self.degreesFacing) * constants.LAZER_SPEED
        self.position[1] += math.sin(self.degreesFacing) * constants.LAZER_SPEED

        self.endPoint = (
            self.position[0] + (math.cos(self.degreesFacing) * constants.LAZER_LENGTH),
            self.position[1] + (math.sin(self.degreesFacing) * constants.LAZER_LENGTH)
        )

        topLeftX, topLeftY = self.get_top_left()
        
        bottomRightX, bottomRightY = self.get_bottom_right()

        collisionSurface = pygame.Surface((
            math.ceil(bottomRightX - topLeftX),
            math.ceil(bottomRightY - topLeftY)
        ))

        pygame.draw.line(
            collisionSurface, 
            constants.LAZER_COLOR,
            (math.ceil(self.position[0] - topLeftX), math.ceil(self.position[1] - topLeftY)),
            (math.ceil(self.endPoint[0] - topLeftX), math.ceil(self.endPoint[1] - topLeftY))
        )

        lineMask = pygame.mask.from_surface(collisionSurface)

        collided = lineMask.overlap(
            playerMask,
            (playerPos[0] - topLeftX + tilesOffset,
             playerPos[1] - topLeftY)
        )

        return collided
    

    def check_offscreen(self, tilesOffset, playerRoom, rooms):
        topLeftX, topLeftY = self.get_top_left()
        bottomRightX, bottomRightY = self.get_bottom_right()

        startOfLevel = -(playerRoom * constants.SCREEN_SIZE[0]) + tilesOffset
        endOfLevel = startOfLevel + (rooms * constants.SCREEN_SIZE[0])

        xOffScreen = bottomRightX < startOfLevel or topLeftX > endOfLevel
        yOffScreen = bottomRightY < 0 or topLeftY > constants.SCREEN_SIZE[1]

        return xOffScreen or yOffScreen

    
    def render(self, window):
        pygame.draw.line(
            window, 
            constants.LAZER_COLOR,
            self.position,
            self.endPoint
        )


class Belloq:
    def __init__(self):
        self.lazers = []
        self.cooldown = constants.BELLOQ_COOLDOWN

        self.animation = {}
        for name, data in constants.BELLOQ_ANIMATIONS.items():
            self.animation[name] = src.animation.Animation(
                data["delay"],
                path = data["path"],
                frames = data["frames"]
            )
        self.currentAnim = "idle"
        self.reset()


    def reset(self):
        self.switchAnim("idle")
        self.position = [
            -self.animation[self.currentAnim].get_frame().get_width(), 
            constants.SCREEN_SIZE[1] // 2 - self.animation[self.currentAnim].get_frame().get_height() // 2
        ]
        self.lazers.clear()
        self.cooldown = constants.BELLOQ_COOLDOWN

    
    def switchAnim(self, newAnim):
        if newAnim != self.currentAnim:
            self.currentAnim = newAnim
            self.animation[self.currentAnim].reset()


    def create_lazer(self, player, playerScreenX):
        playerCenter = (
            playerScreenX + constants.PLAYER_WIDTH // 2,
            player.rect.y + player.rect.height // 2
        )

        eyeballCenter = (
            self.screenPosition[0] + constants.BELLOQ_LAZER_OFFSET[0],
            self.screenPosition[1] + constants.BELLOQ_LAZER_OFFSET[1]
        )

        randomOffsetDegrees = random.randrange(
            -constants.BELLOQ_LAZER_ACCURACY * 100, 
            constants.BELLOQ_LAZER_ACCURACY * 100
        ) / 100

        # Creating a lazer pointing at the player
        self.lazers.append(Lazer(
            math.atan2( # Finds the rotation needed to point at the player
                playerCenter[1] - eyeballCenter[1],
                playerCenter[0] - eyeballCenter[0]
            ) + randomOffsetDegrees,
            eyeballCenter # Starting position
        ))

    
    def update(self, player, playerRoom, amountOfRooms, tilesOffset):
        self.screenPosition = self.position.copy()
        self.screenPosition[0] += tilesOffset
        self.screenPosition[0] -= playerRoom * constants.SCREEN_SIZE[0]

        playerScreenX = player.rect.x + tilesOffset


        img = self.animation[self.currentAnim].get_frame()

        if playerScreenX < self.screenPosition[0] + (img.get_width() / 2):
            self.position[1] += (player.rect.y - (self.screenPosition[1] + img.get_height() / 2)) / 25
            
            self.position[0] += (playerScreenX - (self.screenPosition[0] + img.get_width() / 2)) / 25
        
        else:
            self.position[0] += constants.BELLOQ_SPEED

        self.cooldown -= 1

        if self.cooldown <= 0:
            self.cooldown = constants.BELLOQ_COOLDOWN
            self.switchAnim("attack")

        animationContinue = self.animation[self.currentAnim].update() 
        if not animationContinue: # If the animation finished

            if self.currentAnim == "attack":
                self.switchAnim("idle")

                self.create_lazer(player, playerScreenX)
        
        for lazer in self.lazers:
            if lazer.update(player.get_mask(), player.rect.topleft, tilesOffset):
                # Collided with player
                return True
        
        # Removing lazers that are offscreen
        self.lazers[:] = [lazer for lazer in self.lazers if not lazer.check_offscreen(tilesOffset, playerRoom, amountOfRooms)] 

        # Checking collisions between the Belloq and the player
        belloqMask = pygame.mask.from_surface(self.animation[self.currentAnim].get_frame())
        playerMask = player.get_mask()

        collided = belloqMask.overlap(
            playerMask,
            (playerScreenX - self.screenPosition[0],
            player.rect.y - self.screenPosition[1])
        )
        
        if collided:
            return True
    

    def render(self, window):
        self.animation[self.currentAnim].render(window, self.screenPosition)

        for lazer in self.lazers:
            lazer.render(window)