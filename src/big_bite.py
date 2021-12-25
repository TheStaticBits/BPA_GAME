import pygame
import random

import src.constants as constants
import src.animation

"""
This class manages the Big Bite boss (second boss).
"""
class BigBite:
    # Sets up the animation and the default variables
    def __init__(self):
        self.animation = src.animation.Animation(
            constants.BIG_BITE_DELAY,
            path = constants.BIG_BITE_ANIM_PATH,
            frames = constants.BIG_BITE_TOTAL_FRAMES
        )

        self.reset()
    

    # Resets the boss to default
    def reset(self):
        self.delayCounter = random.randint(constants.BIG_BITE_ATTACK_DELAY[0], constants.BIG_BITE_ATTACK_DELAY[1]) # For counting the frames between the attacks
        self.attacking = False

        self.position = None
        self.room = None # The room number the boss was created in


    # Updates the boss, checking for collisions and also updating cooldowns
    def update(
        self, 
        playerMask, # The player's mask object
        playerPosition, # The player's position in the level
        tilesOffset, # The offset of the level
        room # The room number the player is in
        ):
        if not self.attacking: # If the boss is not on screen
            self.delayCounter -= 1

            if self.delayCounter <= 0:
                # Choosing a random delay in the range given in constants for the next time
                self.delayCounter = random.randint(constants.BIG_BITE_ATTACK_DELAY[0], constants.BIG_BITE_ATTACK_DELAY[1])
                self.attacking = True

                self.animation.reset()

                # Choosing a random position on screen
                self.position = (
                    random.randint(0, constants.SCREEN_SIZE[0] - self.animation.get_image_width()) - tilesOffset,
                    random.randint(0, constants.SCREEN_SIZE[1] - self.animation.get_image_height())
                )

                self.room = room
        
        else:
            if not self.animation.update(): # If the animation ended
                self.attacking = False

            # If the animation is on the frame where the Big Bite attacks
            if self.animation.frame == constants.BIG_BITE_ATTACK_FRAME:
                # Mask from the animation
                bbMask = pygame.mask.from_surface(self.animation.get_frame())

                # Position on screen
                onScreenX = self.position[0] + tilesOffset - ((room - self.room) * constants.SCREEN_SIZE[0])
                
                # COllision CHECKING yay
                collided = bbMask.overlap(
                    playerMask, 
                    (playerPosition[0] + tilesOffset - onScreenX, 
                     playerPosition[1] - self.position[1])
                )

                return collided
        
    
    # Renders animation frame if the boss is attacking
    def render(self, window, tilesOffset, playerRoom):
        if self.attacking:
            self.animation.render(
                window, 
                (self.position[0] + tilesOffset - ((playerRoom - self.room) * constants.SCREEN_SIZE[0]), 
                 self.position[1])
            )