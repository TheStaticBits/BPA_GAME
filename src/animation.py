import pygame

import src.utility as utility

"""
This class, Animation, handles the animation.
It has several functions which updates the animation, renders the frame, gets the frame image, and more.
It also loads the animation by itself.
"""
class Animation:
    # Loads the spritesheet with the appropriate inputs, creates default variables
    def __init__(
        self, 
        delay, # Delay between frames
        path = None, # Path of the image
        width = None, # Width of one frame
        frames = None # Frames in the image
        # The load_spritesheet function only requires either frames or width
        # So any instances of this class can be created with one or the other
        ):
        if path is not None:
            self.images = utility.load_spritesheet(
                path, 
                width = width, 
                frames = frames
            )

        self.delay = delay

        self.timer = 0
        self.frame = 0

    # Updates the frames, returns False if the animation ended
    def update(self) -> bool:
        self.timer += 1

        if self.timer >= self.delay:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = 0
                return False # If the animation is finished

        return True
    
    
    # Renders the frame to the window, at a given position
    def render(self, window, position):
        window.blit(self.images[self.frame], position)
    

    # Gets the current pygame.Surface frame
    def get_frame(self) -> "pygame.Surface":
        return self.images[self.frame]
    

    # Gets the width of the current frame
    def get_image_width(self) -> int:
        return self.images[self.frame].get_width()

    
    # Gets the height of the current frame
    def get_image_height(self) -> int:
        return self.images[self.frame].get_height()
    
    
    # Sets the alpha value for all frames to a given alpha value
    def set_alpha(self, alpha):
        for image in self.images:
            image.set_alpha(alpha)
    

    # Creates a copy of the animation
    def copy(self) -> "Animation":
        obj = Animation(self.delay)
        obj.images = self.images
        return obj
    
    # Resets the frame and timer
    def reset(self):
        self.frame = 0
        self.timer = 0