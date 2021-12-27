import pygame

import src.utility as utility

class Animation:
    """
    This class, Animation, handles the animation.
    It has several functions which updates the animation, renders the frame, gets the frame image, and more.
    It also loads the animation by itself.
    """
    def __init__(
        self, 
        delay, # Delay between frames
        path = None, # Path of the image
        width = None, # Width of one frame
        frames = None # Frames in the image
        # The load_spritesheet function only requires either frames or width
        # So any instances of this class can be created with one or the other
        ):
        """Loads the spritesheet with the appropriate inputs, creates default variables"""
        if path is not None:
            self.images = utility.load_spritesheet(
                path, 
                width = width, 
                frames = frames
            )

        self.delay = delay

        self.timer = 0
        self.frame = 0


    def update(self) -> bool:
        """Updates the frames, returns False if the animation ended"""
        self.timer += 1

        if self.timer >= self.delay:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = 0
                return False # If the animation is finished

        return True
    
    
    def render(self, window, position):
        """Renders the frame to the window, at a given position"""
        window.blit(self.images[self.frame], position)
    

    def get_frame(self) -> "pygame.Surface":
        """Gets the current pygame.Surface frame in the animation"""
        return self.images[self.frame]
    

    def get_image_width(self) -> int:
        """Gets the width of the current frame"""
        return self.images[self.frame].get_width()

    
    def get_image_height(self) -> int:
        """Gets the height of the current frame"""
        return self.images[self.frame].get_height()
    
    
    def set_alpha(self, alpha):
        """Sets the alpha value for all frames to a given alpha value"""
        for image in self.images:
            image.set_alpha(alpha)
    

    def copy(self) -> "Animation":
        """Creates a copy of the animation"""
        obj = Animation(self.delay)
        obj.images = self.images
        return obj
    

    def reset(self):
        """Resets the frame and timer"""
        self.frame = 0
        self.timer = 0