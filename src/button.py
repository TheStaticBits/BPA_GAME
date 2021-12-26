import pygame
import math

import src.constants as constants

class Button:
    """
    Button class, for all buttons on screen. 
    Handles updating/checking, and rendering.
    """
    def __init__(
        self, 
        centerX, # Position where the button will be centered on
        y, # Y position
        
        # If the button is being created from text
        fontObj = None, 
        text = None,
        textOffset = None, # Amount rectangle expands backwards behind the text
        
        # If the button is being created from an image
        imagePath = None, # or
        image = None
        ):
        """Initiates all general variables, also creating the rectangle used for collision"""

        self.isText = text is not None

        if self.isText:
            self.text = text
            self.fontObj = fontObj

            self.textOffset = textOffset

            self.fontRendered = fontObj.render(text, False, constants.WHITE) # Used to get the width of the text area
            # Creating rectangle getting width and height from the rendered text
            self.rect = pygame.Rect((
                centerX - (self.fontRendered.get_width() + self.textOffset) / 2,
                y,
                self.fontRendered.get_width() + self.textOffset, 
                self.fontRendered.get_height()
            ))
        
        else:
            # This image needs to have the contents of the button,
            # (what is displayed when the button is idling), as white
            # while the background should be black
            if image is not None:
                self.image = image
            else:
                self.image = pygame.image.load(imagePath).convert()

            # Centers x, gets width and height of the image as the rect for the button
            self.rect = pygame.Rect((
                centerX - self.image.get_width() / 2,
                y,
                self.image.get_width(),
                self.image.get_height()
            ))

        self.reset() # Sets up other variables to default states

    
    def reset(self):
        """Resets button to the default state"""
        self.selected = False # If the mouse is hovering over the button
        self.clicked = False # The button activates when you let go of it
        self.highlightYPos = 0

    
    def update(self, mousePos, mouseInputs) -> bool:
        """Updates and checks for a collision. Returns True if the user clicked and then let go. Also updates the animation that plays for the button."""
        self.selected = self.rect.collidepoint(mousePos)

        if self.selected:
            if mouseInputs["left"]:
                self.clicked = True

            else:
                if self.clicked:
                    self.reset()
                    return True
                    
        else:
            self.clicked = False

        if self.selected and not self.clicked:
            # Increases the y position rapidly if it's far away from the top
            # and slowly as it gets to the top
            self.highlightYPos += (self.rect.height - self.highlightYPos) / constants.BUTTON_HIGHLIGHT_SPEED
        
        else:
            # Reverse effect, goes to zero
            self.highlightYPos -= self.highlightYPos / constants.BUTTON_HIGHLIGHT_SPEED
        
        return False


    def render(self, window):
        """Renders the button with its highlight effect"""
        if round(self.highlightYPos) != 0: # If it's highlighted at least partially
            cielHYPos = math.ceil(self.highlightYPos) # Rounded up highlighted y position

            # Top section of the button, the "normal" part
            topHalf = pygame.Surface((self.rect.width, self.rect.height - cielHYPos))
            # Bottom section, the reversed and "highlighted" part
            highlighted = pygame.Surface((self.rect.width, cielHYPos), flags = pygame.SRCALPHA)

            if self.isText:
                # Text
                topHalf.blit(self.fontRendered, (self.textOffset, 0)) # Rendering text
                topHalf.set_colorkey(constants.BLACK) # Removes black background

                highlighted.fill(constants.WHITE)

                # Getting the text surface but black
                blackFont = self.fontObj.render(self.text, False, constants.BLACK)
                # Rendering onto the highlighted surface, up above it so it only shows the bottom section (or however much is highlighted) of the text
                highlighted.blit(blackFont, (self.textOffset, -(self.rect.height - cielHYPos)))
                highlighted.set_colorkey(constants.BLACK) # Makes the text part transparent
            
            else:
                # Image

                # Normal top section rendering
                topHalf.blit(self.image, (0, 0))
                topHalf.set_colorkey(constants.BLACK)

                # Copies image and makes the white part transparent
                noWhite = self.image.copy()
                noWhite.set_colorkey(constants.WHITE)

                # Creates a copy of the image with no white, but this time solidifying the colorkey so the pixelarray doesn't see the white section of the image
                reversed = pygame.Surface(noWhite.get_size(), flags = pygame.SRCALPHA)
                reversed.blit(noWhite, (0, 0))

                # Turns the black background to white
                pixelArr = pygame.PixelArray(reversed)
                pixelArr.replace(constants.BLACK, constants.WHITE)
                del pixelArr

                # Drawing onto the highlighted section
                highlighted.blit(reversed, (0, -(self.rect.height - cielHYPos)))
                

            # Rendering both sections
            window.blit(topHalf, self.rect.topleft)
            window.blit(highlighted, (self.rect.x, self.rect.y + (self.rect.height - cielHYPos)))

        
        else:
            # Rendering normally

            if self.isText:
                # Text
                window.blit(self.fontRendered, (self.rect.x + self.textOffset, self.rect.y))
            
            else:
                # Image
                noBG = self.image.copy() # Copying
                noBG.set_colorkey(constants.BLACK) # Setting the background to transparent
                window.blit(noBG, self.rect.topleft)