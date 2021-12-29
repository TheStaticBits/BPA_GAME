import pygame
import logging

import src.button
import src.constants as constants

class PauseMenu():
    """
    Handles the entire pause menu, including the pause button on other scenes
    """
    def __init__(self):
        """Sets up logger and buttons and other variables"""
        self.logger = logging.getLogger(__name__) # Logger

        font = pygame.font.Font(constants.FONT_PATH, 25)

        # There Is Nothing logo
        self.logo = pygame.image.load(constants.TIN_LOGO_PATH).convert_alpha()

        # Button layout
        buttons = {
            "resume": (120, "Resume"),
            "restart": (150, "Restart Level"),
            "mainMenu": (180, "Main Menu")
        }

        # Iterating through button layout and creating the button objects
        self.buttons = {}
        for name, values in buttons.items():
            self.buttons[name] = src.button.Button(
                constants.SCREEN_SIZE[0] / 2,
                values[0],
                fontObj = font,
                text = values[1],
                textOffset = 1
            )
        
        # Pause button in the top left
        self.pauseButton = src.button.Button(
            8, 0,
            imagePath = constants.PAUSE_BUTTON_PATH,
        )

        self.background = None
        self.level = None

        self.levelFont = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE)
    

    def render_pause_button(self, window):
        """Renders the pause button to the window"""
        self.pauseButton.render(window)


    def check_for_pause(self, inputs, mousePos, mouseInputs) -> bool:
        """Returns true if escape or the pause button has been pressed"""
        return inputs["esc"] or self.pauseButton.update(mousePos, mouseInputs)

    
    def update_info(self, background, level, room, levelLength):
        """Changes the background which is rendered behind the pause menu. Pass in a surface with the point at which the game was paused at. Also updates the level and room numbers shown in the top right corner."""
        self.background = background.copy()
        self.background.set_alpha(100) # Alpha 
        self.level = level
        self.room = f"Room {room}/{levelLength}"
    

    def update(self, inputs, mousePos, mouseInputs) -> str:
        """Updates the buttons, returning the button pressed. Also returns "resume" if the escape button has been pressed."""
        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                self.logger.info(f"Pressed {key}")
                return key
        
        if inputs["esc"]:
            self.logger.info("Resuming")
            return "resume"
        
        return "pause"

    
    def render(self, window):
        """Renders buttons, background, and logo to the screen"""
        window.blit(self.background, (0, 0))

        # Rendering buttons
        for button in self.buttons.values():
            button.render(window)
        
        # Rendering logo centered on the x axis
        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))

        # Rendering level number in the top right corner
        text = self.levelFont.render(self.level, False, constants.WHITE)
        window.blit(text, (constants.SCREEN_SIZE[0] - text.get_width() - 10, 10))
        
        if self.level != "Cutscene":
            # Rendering room number in the top right corner
            text = self.levelFont.render(self.room, False, constants.WHITE)
            window.blit(text, (constants.SCREEN_SIZE[0] - text.get_width() - 10, 24))