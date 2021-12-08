import pygame

import src.constants as constants

class Button:
    def __init__(
        self, 
        centerX, 
        y,
        fontObj,
        text,
        textOffset = 0 # Amount rectangle expands backwards behind the text
        ):
        self.text = text
        self.fontObj = fontObj

        self.textOffset = textOffset

        self.fontRendered = fontObj.render(text, False, (255, 255, 255)) # Used to get the width of the text area
        self.rect = pygame.Rect((
            centerX - (self.fontRendered.get_width() + self.textOffset) / 2,
            y,
            self.fontRendered.get_width() + self.textOffset, 
            self.fontRendered.get_height()
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
            text = pygame.Surface((self.rect.width, self.rect.height - self.highlightYPos))
            text.blit(self.fontRendered, (self.textOffset, 0))
            text.set_colorkey((0, 0, 0)) # Removes black background

            highlighted = pygame.Surface((self.rect.width, self.highlightYPos))
            highlighted.fill((255, 255, 255))

            blackFont = self.fontObj.render(self.text, False, (0, 0, 0))
            highlighted.blit(blackFont, (self.textOffset, -(self.rect.height - self.highlightYPos)))
            highlighted.set_colorkey((0, 0, 0)) # Makes the text transparent

            window.blit(text, self.rect.topleft)
            window.blit(highlighted, (self.rect.x, self.rect.y + (self.rect.height - self.highlightYPos)))

        
        else:
            window.blit(self.fontRendered, (self.rect.x + self.textOffset, self.rect.y))