import pygame
import random

import src.utility as utility

class RedStare:
    def __init__(self):
        self.animations = utility.load_animations_dict(constants.RED_STARE_ANIMATIONS)

        self.poppedUp = False
        self.mouthUp = False
        self.bodyPos = [0, constants.SCREEN_SIZE[1]]

        self.cooldown = constants.RED_STARE_COOLDOWN
    
    
    def update(self, player, room, tileOffset):
        for anim in self.animations.values():
            anim.update()

        if not self.poppedUp:
            if self.bodyPos[1] >= constants.SCREEN_SIZE[1]:
                self.bodyPos[1] += constants.RED_STARE_POPUP_SPEED
            
            else:
                self.cooldown -= 1

                if self.cooldown <= 0:
                    self.poppedUp = True

                    playerRoomX = room * constants.SCREEN_SIZE[0] + player.x

                    self.bodyPos = [
                        random.randint(-constants.RED_STARE_POPUP_RANGE, constants.RED_STARE_POPUP_RANGE) + playerRoomX + room * constants.SCREEN_SIZE[0], 
                        constants.SCREEN_SIZE[1]
                    ]

        else:
            if self.bodyPos[1] <= constants.SCREEN_SIZE[1] - self.animations["body"].get_image_height():
                pass

            else:
                self.bodyPos[1] -= constants.RED_STARE_POPUP_SPEED

    
    def render(self, window, tileOffset, room):
        self.animations["body"].render(
            window, 
            (self.bodyPos[0] - room * constants.SCREEN_SIZE[0],
             self.bodyPos[1])
        )

        self.animations["mouth"].render()