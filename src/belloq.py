import pygame
import logging
import random
import math

import src.constants as constants
import src.utility as utility

class Lazer:
    """
    This class, lazer, manages the lazers that the Belloq fires.
    It has several functions that can check collisions with the player, check if it's offscreen, and more.
    """
    def __init__(
        self, 
        degreesFacing, # What direction it's facing in radians 
        startPos 
        ):
        """Sets the default vars"""
        self.degreesFacing = degreesFacing
        self.position = list(startPos)
    
    
    def get_top_left(self, position):
        """Gets the lessor of the two points, for the top left"""
        topLeftX = position[0] if position[0] < self.endPoint[0] else self.endPoint[0]
        topLeftY = position[1] if position[1] < self.endPoint[1] else self.endPoint[1]
        return (topLeftX, topLeftY)
    

    def get_bottom_right(self, position):
        """Gets the greater of the two points, for the bottom right"""
        bottomRightX = position[0] if position[0] > self.endPoint[0] else self.endPoint[0]
        bottomRightY = position[1] if position[1] > self.endPoint[1] else self.endPoint[1]
        return(bottomRightX, bottomRightY)
    

    def update(self, playerMask, playerPos, playerRoom, tilesOffset) -> bool:
        """Updates the lazer, returning True if it has collided with the player"""
        # Moves the lazer in the direction it's moving
        self.position[0] += math.cos(self.degreesFacing) * constants.LAZER_SPEED
        self.position[1] += math.sin(self.degreesFacing) * constants.LAZER_SPEED

        self.screenPos = self.position.copy()
        self.screenPos[0] += tilesOffset - playerRoom * constants.SCREEN_SIZE[0]

        # The end point of the lazer (self.position is the starting point of it)
        self.endPoint = (
            self.screenPos[0] + (math.cos(self.degreesFacing) * constants.LAZER_LENGTH),
            self.screenPos[1] + (math.sin(self.degreesFacing) * constants.LAZER_LENGTH)
        )

        topLeftX, topLeftY = self.get_top_left(self.screenPos)
        bottomRightX, bottomRightY = self.get_bottom_right(self.screenPos)

        # Creates a surface with the exact size of the lazer
        # Used to create a mask to check collisions with the player
        collisionSurface = pygame.Surface((
            math.ceil(bottomRightX - topLeftX),
            math.ceil(bottomRightY - topLeftY)
        ))

        # Draws the lazer onto the collision surface
        pygame.draw.line(
            collisionSurface, 
            constants.LAZER_COLOR,
            (math.ceil(self.screenPos[0] - topLeftX), math.ceil(self.screenPos[1] - topLeftY)),
            (math.ceil(self.endPoint[0] - topLeftX), math.ceil(self.endPoint[1] - topLeftY))
        )

        lineMask = pygame.mask.from_surface(collisionSurface)

        # Checking collisions between the lazer and the player
        collided = lineMask.overlap(
            playerMask,
            (playerPos[0] - topLeftX + tilesOffset,
             playerPos[1] - topLeftY)
        )

        return collided
    

    def check_offscreen(self, rooms) -> bool:
        """Checks if it's off the screen of the entire level and returns True if it is"""
        topLeftX, topLeftY = self.get_top_left(self.position)
        bottomRightX, bottomRightY = self.get_bottom_right(self.position)

        endOfLevel = rooms * constants.SCREEN_SIZE[0]

        xOffScreen = bottomRightX < 0 or topLeftX > endOfLevel
        yOffScreen = bottomRightY < 0 or topLeftY > constants.SCREEN_SIZE[1]

        return xOffScreen or yOffScreen

    
    def render(self, window):
        """Draws the line to the screen, from the starting position to the ending position"""
        pygame.draw.line(
            window, 
            constants.LAZER_COLOR,
            self.screenPos,
            self.endPoint
        )


class Belloq:
    """
    This manages the Belloq boss, creating lazers, moving it, 
    checking collisions with the player, and rendering it.
    """
    def __init__(self):
        """Loads animation, sets default variables"""
        self.logger = logging.getLogger(__name__)

        self.lazers = []
        self.cooldown = constants.BELLOQ_COOLDOWN

        self.animation = utility.load_animations_dict(constants.BELLOQ_ANIMATIONS)
        self.currentAnim = "idle"
        self.reset()


    def reset(self):
        """Resets the boss to its default position and state, clearing lazers"""
        self.logger.info("Resetting Belloq boss")

        self.switchAnim("idle")
        self.position = [
            -self.animation[self.currentAnim].get_image_width(), 
            constants.SCREEN_SIZE[1] // 2 - self.animation[self.currentAnim].get_image_height() // 2
        ]
        self.lazers.clear()
        self.cooldown = constants.BELLOQ_COOLDOWN

    
    def switchAnim(self, newAnim):
        """Switches to a new animation if the previous animation wasn't the same"""
        if newAnim != self.currentAnim:
            self.currentAnim = newAnim
            self.animation[self.currentAnim].reset()


    def create_lazer(self, player, playerScreenX, screenPos):
        """Creates a lazer object, starting at the eye and pointing in the direction of the player with a random offset"""
        self.logger.info("Creating lazer")

        playerCenter = (
            playerScreenX + constants.PLAYER_WIDTH // 2,
            player.rect.y + player.rect.height // 2
        )

        eyeballCenter = (
            self.position[0] + constants.BELLOQ_LAZER_OFFSET[0],
            self.position[1] + constants.BELLOQ_LAZER_OFFSET[1]
        )

        eyeballCenterScreenPos = (
            screenPos[0] + constants.BELLOQ_LAZER_OFFSET[0],
            screenPos[1] + constants.BELLOQ_LAZER_OFFSET[1]
        )
        
        # Gets a random decimal (multiplies by 100 to choose a random integer and then divides the result by 100)
        # Since the degrees is in radians
        randomOffsetDegrees = random.randrange(
            -constants.BELLOQ_LAZER_ACCURACY * 100, 
            constants.BELLOQ_LAZER_ACCURACY * 100
        ) / 100

        # Creating a lazer pointing at the player
        self.lazers.append(Lazer(
            utility.angle_to(eyeballCenterScreenPos, playerCenter) + randomOffsetDegrees,
            # math.atan2( # Finds the rotation needed to point at the player
            #     playerCenter[1] - eyeballCenterScreenPos[1],
            #     playerCenter[0] - eyeballCenterScreenPos[0]
            # ) + randomOffsetDegrees,
            eyeballCenter # Starting position
        ))

    
    def update(self, player, playerRoom, amountOfRooms, tilesOffset):
        """Updates everything, moves the boss towards the player, the cooldown for lazers, and updating lazers and removing ones offscreen."""
        screenPos = self.position.copy()
        screenPos[0] += tilesOffset
        screenPos[0] -= playerRoom * constants.SCREEN_SIZE[0]

        playerScreenX = player.rect.x + tilesOffset

        # If the player has moved BEHIND the Belloq
        if playerScreenX < screenPos[0] + (self.animation[self.currentAnim].get_image_width() / 2):
            # Moves towards the player quickly, and when reaching the player, slows down
            # Gets the distance between them and divides by 25
            self.position[1] += (player.rect.y - (screenPos[1] + self.animation[self.currentAnim].get_image_height() / 2)) / 25
            self.position[0] += (playerScreenX - (screenPos[0] + self.animation[self.currentAnim].get_image_width() / 2)) / 25
        
        else:
            # Inch the Belloq forward
            self.position[0] += constants.BELLOQ_SPEED

        self.cooldown -= 1

        if self.cooldown <= 0:
            self.logger.info("Starting attack")
            self.cooldown = constants.BELLOQ_COOLDOWN
            self.switchAnim("attack")

        animationContinue = self.animation[self.currentAnim].update() 
        if not animationContinue: # If the animation finished
            # Fires a lazer at the end of the attack animation
            if self.currentAnim == "attack":
                self.switchAnim("idle")

                self.create_lazer(player, playerScreenX, screenPos)
        
        # Checking lazer collisions with the player
        for lazer in self.lazers:
            if lazer.update(player.get_mask(), player.rect.topleft, playerRoom, tilesOffset):
                # Collided with player
                return True
        
        # Removing lazers that are offscreen
        self.lazers[:] = [lazer for lazer in self.lazers if not lazer.check_offscreen(amountOfRooms)] 

        # Checking collisions between the Belloq and the player
        belloqMask = pygame.mask.from_surface(self.animation[self.currentAnim].get_frame())
        playerMask = player.get_mask()

        collided = belloqMask.overlap(
            playerMask,
            (playerScreenX - screenPos[0],
            player.rect.y - screenPos[1])
        )
        
        if collided:
            return True
    

    def render(self, window, tilesOffset, playerRoom):
        """Renders animation frame and lazers"""
        self.animation[self.currentAnim].render(
            window, 
            (self.position[0] + tilesOffset - (playerRoom * constants.SCREEN_SIZE[0]),
             self.position[1])
        )

        for lazer in self.lazers:
            lazer.render(window)