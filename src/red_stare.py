import pygame
import random
import math

import src.utility as utility
import src.constants as constants

class RedStare:
    def __init__(self):
        self.animations = utility.load_animations_dict(constants.RED_STARE_ANIMATIONS)

        self.reset()


    def reset_mouth(self):
        self.mouthStart = None
        self.mouthGoTo = None
        self.mouthDegree = None
        self.mouthGoingBack = False
        self.mouthMoving = False

    
    def reset(self):
        self.poppedUp = False
        self.bodyPos = None
        self.cooldown = constants.RED_STARE_COOLDOWN
        self.mouthPos = None

        self.reset_mouth()

    
    def update(self, player, room, tilesOffset):
        for anim in self.animations.values():
            anim.update()

        if not self.poppedUp:
            if self.bodyPos is None or self.bodyPos[1] > constants.SCREEN_SIZE[1] - constants.RED_STARE_MOUTH_OFFSET[1]:
                self.cooldown -= 1

                if self.cooldown <= 0:
                    self.poppedUp = True

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
            
            else:
                self.bodyPos[1] += constants.RED_STARE_POPUP_SPEED
                self.mouthPos[1] += constants.RED_STARE_POPUP_SPEED

        else:
            if self.mouthMoving:
                totalDis = utility.distance_to(self.mouthStart, self.mouthGoTo)
                currDis = utility.distance_to(self.mouthPos, self.mouthGoTo)

                if currDis <= totalDis / 2:
                    distFromEitherSide = currDis
                
                else:
                    distFromEitherSide = totalDis - currDis
                    distFromEitherSide = max(0, distFromEitherSide)

                velocity = distFromEitherSide / 15 + constants.RED_STARE_MOUTH_SPEED

                self.mouthPos[0] += math.cos(self.mouthDegree) * velocity
                self.mouthPos[1] += math.sin(self.mouthDegree) * velocity

                if round(currDis) == 0:
                    if not self.mouthGoingBack:
                        self.mouthGoingBack = True

                        self.mouthGoTo = (
                            self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                            self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                        )

                        self.mouthStart = self.mouthPos[:]

                        self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)
                    
                    else:
                        self.reset_mouth()
                        
                        self.poppedUp = False
                        self.cooldown = constants.RED_STARE_COOLDOWN

            else:
                self.bodyPos[1] -= constants.RED_STARE_POPUP_SPEED
                self.mouthPos[1] -= constants.RED_STARE_POPUP_SPEED

                self.mouthPos = [
                    self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                    self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                ]

                # If the body has fully appeared on screen
                if self.bodyPos[1] <= constants.SCREEN_SIZE[1] - self.animations["body"].get_image_height():
                    self.mouthMoving = True

                    self.mouthStart = self.mouthPos[:]

                    # Centers the mouth onto the player
                    self.mouthGoTo = (
                        room * constants.SCREEN_SIZE[0] + player.rect.x + player.rect.width / 2 - self.animations["mouth"].get_image_width() / 2,
                        player.rect.y + player.rect.height / 2 - self.animations["mouth"].get_image_height() / 2
                    )

                    self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)
            
        if self.mouthPos is not None:
            pScreenX = player.rect.x + tilesOffset
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