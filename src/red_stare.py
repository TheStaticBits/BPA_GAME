import pygame
import logging
import random
import math

import src.utility as utility
import src.constants as constants

class RedStare:
    """
    Red Stare boss (appears in level 19). 
    Instance of this is created in the boss_level.py file.
    Handles everything related to the boss.
    """

    def __init__(self): 
        """Sets up variables and loads animations"""
        self.logger = logging.getLogger(__name__)

        self.animations = utility.load_animations_dict(constants.RED_STARE_ANIMATIONS)

        self.reset()

    
    def reset_mouth(self): 
        """Resets the mouth related variables"""
        self.logger.info("Resetting mouth")
        self.mouthStart = None
        self.mouthGoTo = None
        self.mouthDegree = None
        self.mouthGoingBack = False
        self.mouthMoving = False

    
    def reset(self):
        """Resets all general variables to the default state"""
        self.logger.info("Resetting Red Stare boss")
        self.poppedUp = False
        self.bodyPos = None
        self.cooldown = constants.RED_STARE_COOLDOWN
        self.mouthPos = None

        self.reset_mouth()

    
    def update(self, player, room, tilesOffset):
        """Updates the boss, moving it if it is moving. Also checks for collisions between the boss and the player."""
        # Updating animations
        for anim in self.animations.values():
            anim.update()

        if not self.poppedUp: # If it is moving down or below the screen

            # If the boss is below the screen, update the countdown
            if self.bodyPos is None or self.bodyPos[1] > constants.SCREEN_SIZE[1] - constants.RED_STARE_MOUTH_OFFSET[1]:
                self.cooldown -= 1

                if self.cooldown <= 0: # If the boss is now going to activate and move up
                    self.logger.info("Popping up")

                    self.poppedUp = True

                    # Since the player.rect.x is the x position of the player in the given "room",
                    # add rooms that the player has already gone through 
                    playerRoomX = room * constants.SCREEN_SIZE[0] + player.rect.x

                    randomOffset = random.randint(-constants.RED_STARE_POPUP_RANGE, constants.RED_STARE_POPUP_RANGE)

                    self.bodyPos = [
                        playerRoomX + randomOffset, 
                        constants.SCREEN_SIZE[1] - constants.RED_STARE_MOUTH_OFFSET[1]
                    ]
                    
                    self.mouthPos = [
                        self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                        self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                    ]
            
            else: # If the boss still needs to move down off the screen
                self.bodyPos[1] += constants.RED_STARE_POPUP_SPEED
                self.mouthPos[1] += constants.RED_STARE_POPUP_SPEED

        else: # If the boss is moving up or attacking
            if self.mouthMoving: # If the mouth is attacking
                # Finds the distance between the mouth's starting and ending point
                totalDis = utility.distance_to(self.mouthStart, self.mouthGoTo)
                # Finds the distance the mouth still has to go
                currDis = utility.distance_to(self.mouthPos, self.mouthGoTo)

                if currDis <= totalDis / 2:
                    # Mouth is closest to the starting point
                    distFromEitherSide = currDis
                
                else:
                    # Mouth is closest to the ending point
                    distFromEitherSide = totalDis - currDis
                    distFromEitherSide = max(0, distFromEitherSide) # Setting it to zero if it's negative

                # Calculates velocity so that it's the greatest when the mouth is in the center of its path
                velocity = distFromEitherSide / 15 + constants.RED_STARE_MOUTH_SPEED

                # Moving by degree, with velocity
                self.mouthPos[0] += math.cos(self.mouthDegree) * velocity
                self.mouthPos[1] += math.sin(self.mouthDegree) * velocity

                if round(currDis) == 0: # If the mouth reached its end point
                    if not self.mouthGoingBack:
                        self.logger.info("Reversing direction")
                        # If the mouth needs to turn back to the body
                        self.mouthGoingBack = True

                        self.mouthGoTo = (
                            self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                            self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                        )

                        self.mouthStart = self.mouthPos[:]

                        self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)
                    
                    else: # If the mouth's attack has finished
                        self.logger.info("Mouth attack finished")

                        # Resetting
                        self.reset_mouth()
                        
                        self.poppedUp = False
                        self.cooldown = constants.RED_STARE_COOLDOWN

            else: # If the mouth isn't attacking
                # Move the body and mouth up
                self.bodyPos[1] -= constants.RED_STARE_POPUP_SPEED
                self.mouthPos[1] -= constants.RED_STARE_POPUP_SPEED

                # If the body has fully appeared on screen
                if self.bodyPos[1] <= constants.SCREEN_SIZE[1] - self.animations["body"].get_image_height():
                    self.logger.info("Mouth attack started")
                    self.mouthMoving = True

                    # Used for determining speed later
                    self.mouthStart = self.mouthPos[:]

                    # Centers the mouth onto the player
                    self.mouthGoTo = (
                        (room * constants.SCREEN_SIZE[0] + player.rect.x) + player.rect.width / 2 - self.animations["mouth"].get_image_width() / 2,
                        player.rect.y + player.rect.height / 2 - self.animations["mouth"].get_image_height() / 2
                    )

                    # Direction it's moving in
                    self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)
            
        # Checking collisions between the mouth and the player
        if self.mouthPos is not None:
            pScreenX = player.rect.x + tilesOffset
            # Boss on screen x position
            # The mouthPos is the position from the very start of the level
            bScreenX = self.mouthPos[0] + tilesOffset - room * constants.SCREEN_SIZE[0]

            mask = pygame.mask.from_surface(self.animations["mouth"].get_frame())
            playerMask = player.get_mask()

            collided = mask.overlap(
                playerMask, 
                (pScreenX - bScreenX, 
                player.rect.y - self.mouthPos[1])
            )
            
            return collided
            
        return False

    
    def render(self, window, tilesOffset, room):
        """Renders the boss along with its mouth on screen"""
        if self.bodyPos is not None:
            offset = tilesOffset - room * constants.SCREEN_SIZE[0]

            self.animations["body"].render(
                window, 
                (self.bodyPos[0] + offset,
                self.bodyPos[1])
            )

            if self.mouthMoving:
                self.animations["mouth"].render(
                    window,
                    (self.mouthPos[0] + offset,
                    self.mouthPos[1])
                )
            
            else:
                self.animations["mouth"].render(
                    window,
                    (self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0] + offset,
                    self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1])
                )