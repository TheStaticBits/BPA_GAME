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
        self.mouthPos = None
        self.mouthGoTo = None
        self.mouthDegree = None
        self.mouthGoingBack = False
        self.mouthPastPointOffset = None
        self.mouthMoving = False

    
    def reset(self):
        self.poppedUp = False
        self.bodyPos = None
        self.cooldown = constants.RED_STARE_COOLDOWN

        self.reset_mouth()

    
    def update(self, player, room):
        for anim in self.animations.values():
            anim.update()

        if not self.poppedUp:
            if self.bodyPos is None or self.bodyPos[1] > constants.SCREEN_SIZE[1]:
                self.cooldown -= 1

                if self.cooldown <= 0:
                    self.poppedUp = True

                    playerRoomX = room * constants.SCREEN_SIZE[0] + player.rect.x

                    self.bodyPos = [
                        random.randint(-constants.RED_STARE_POPUP_RANGE, constants.RED_STARE_POPUP_RANGE) + playerRoomX + room * constants.SCREEN_SIZE[0], 
                        constants.SCREEN_SIZE[1]
                    ]
            
            else:
                self.bodyPos[1] += constants.RED_STARE_POPUP_SPEED

        else:
            if self.mouthMoving:
                self.mouthPos[0] += math.cos(self.mouthDegree) * 5
                self.mouthPos[1] += math.sin(self.mouthDegree) * 5

                # Testing to see if the mouth has moved past the target point
                movedPastX = (self.mouthPastPointOffset[0] and self.mouthPos[0] > self.mouthGoTo[0]) or (not self.mouthPastPointOffset and self.mouthPos[0] < self.mouthGoTo[0])
                movedPastY = (self.mouthPastPointOffset[1] and self.mouthPos[1] > self.mouthGoTo[1]) or (not self.mouthPastPointOffset and self.mouthPos[1] < self.mouthGoTo[1])

                if movedPastX and movedPastY:
                    if not self.mouthGoingBack:
                        self.mouthGoingBack = True

                        self.mouthGoTo = (
                            self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                            self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                        )

                        self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)

                        self.mouthPastPointOffset = (
                            self.mouthGoTo[0] > self.mouthPos[0],
                            self.mouthGoTo[1] > self.mouthPos[1]
                        )
                    
                    else:
                        self.reset_mouth()
                        self.poppedUp = False
                        self.cooldown = constants.RED_STARE_COOLDOWN

            else:
                self.bodyPos[1] -= constants.RED_STARE_POPUP_SPEED

                # If the body has fully appeared on screen
                if self.bodyPos[1] <= constants.SCREEN_SIZE[1] - self.animations["body"].get_image_height():
                    self.mouthMoving = True

                    self.mouthPos = [
                        self.bodyPos[0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                        self.bodyPos[1] + constants.RED_STARE_MOUTH_OFFSET[1]
                    ]

                    self.mouthGoTo = (
                        room * constants.SCREEN_SIZE[0] + player.rect.x,
                        player.rect.y
                    )

                    self.mouthDegree = utility.angle_to(self.mouthPos, self.mouthGoTo)

                    self.mouthPastPointOffset = (
                        self.mouthGoTo[0] > self.mouthPos[0],
                        self.mouthGoTo[1] > self.mouthPos[1]
                    )
        
        return False

    
    def render(self, window, tileOffset, room):
        if self.bodyPos is not None:
            offset = tileOffset - room * constants.SCREEN_SIZE[0]

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