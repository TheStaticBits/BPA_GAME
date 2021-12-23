import pygame

import src.constants as constants

class Button:
    def __init__(
        self, 
        centerX, 
        y,
        # If the button is being created from text
        fontObj = None,
        text = None,
        textOffset = None, # Amount rectangle expands backwards behind the text
        # If the button is being created from an image
        imagePath = None,
        ):
        self.isText = text is not None

        if self.isText:
            self.text = text
            self.fontObj = fontObj

            self.textOffset = textOffset

            self.fontRendered = fontObj.render(text, False, constants.WHITE) # Used to get the width of the text area
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
            self.image = pygame.image.load(imagePath).convert()

            self.rect = pygame.Rect((
                centerX - self.image.get_width() / 2,
                y,
                self.image.get_width(),
                self.image.get_height()
            ))

        self.reset()

    
    def reset(self):
        self.selected = False # If the mouse is hovering over the button
        self.clicked = False # The button activates when you let go of it
        self.highlightYPos = 0

    
    def update(self, mousePos, mouseInputs) -> bool:
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
            self.highlightYPos += (self.rect.height - self.highlightYPos) / constants.BUTTON_HIGHLIGHT_SPEED
        
        else:
            self.highlightYPos -= self.highlightYPos / constants.BUTTON_HIGHLIGHT_SPEED
        
        return False

    def render(self, window):
        if round(self.highlightYPos) != 0:

            topHalf = pygame.Surface((self.rect.width, self.rect.height - self.highlightYPos))
            highlighted = pygame.Surface((self.rect.width, self.highlightYPos), flags = pygame.SRCALPHA)

            if self.isText:
                topHalf.blit(self.fontRendered, (self.textOffset, 0))
                topHalf.set_colorkey(constants.BLACK) # Removes black background

                highlighted.fill(constants.WHITE)

                blackFont = self.fontObj.render(self.text, False, constants.BLACK)
                highlighted.blit(blackFont, (self.textOffset, -(self.rect.height - self.highlightYPos)))
                highlighted.set_colorkey(constants.BLACK) # Makes the text transparent
            
            else:
                topHalf.blit(self.image, (0, 0))
                topHalf.set_colorkey(constants.BLACK)

                noWhite = self.image.copy()
                noWhite.set_colorkey(constants.WHITE)

                reversed = pygame.Surface(noWhite.get_size(), flags = pygame.SRCALPHA)
                reversed.blit(noWhite, (0, 0))

                # Turns the black background to white
                pixelArr = pygame.PixelArray(reversed)
                pixelArr.replace(constants.BLACK, constants.WHITE)
                del pixelArr

                highlighted.blit(reversed, (0, -(self.rect.height - self.highlightYPos)))
                

            window.blit(topHalf, self.rect.topleft)
            window.blit(highlighted, (self.rect.x, self.rect.y + (self.rect.height - self.highlightYPos)))

        
        else:
            # Rendering normally

            if self.isText:
                window.blit(self.fontRendered, (self.rect.x + self.textOffset, self.rect.y))
            
            else:
                noBG = self.image.copy()
                noBG.set_colorkey(constants.BLACK) # Setting the background to transparent
                window.blit(noBG, self.rect.topleft)