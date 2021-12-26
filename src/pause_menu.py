import pygame

import src.button
import src.constants as constants
import src.scene_base

"""
Handles the entire pause menu, including the pause button on other scenes
"""
class PauseMenu(src.scene_base.SceneBase):
    def __init__(self): # Sets up logger and buttons
        super().__init__(__name__) # Logger

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

        # Used for transitions
        self.transitionPos = -constants.SCREEN_SIZE[1] # For sliding down and up
        self.transitionMode = "Into"
        self.transitionAlpha = 255
        self.transitionSceneTo = None

        self.background = None
    

    # Renders the pause button to the window
    def render_pause_button(self, window):
        self.pauseButton.render(window)


    # Returns true if escape or the pause button has been pressed
    def check_for_pause(self, inputs, mousePos, mouseInputs) -> bool:
        return inputs["esc"] or self.pauseButton.update(mousePos, mouseInputs)

    
    # Changes the background which is rendered behind the pause menu
    # Pass in a surface with the point at which it paused at
    def update_background(self, background):
        self.background = background.copy()
        # self.background.set_alpha(100) # Alpha

        self.transitionMode = "into" 
    

    # Transition out of the pause menu
    def transition_out(self, scene):
        self.transitionMode = "out"
        self.transitionSceneTo = scene
    
    
    # Updating transition
    # Returns true when finishing transitioning out
    def update_transition(self) ->:
        if self.transitionMode == "into":
            self.transitionAlpha -= constants.TRANSITION_SPEED
            self.transitionPos += constants.SCREEN_SIZE[1] / (155 / constants.TRANSITION_SPEED)

            if self.transitionAlpha <= 100:
                self.transitionPos = 0
                self.transitionAlpha = 100
        
        elif self.transitionMode == "out":
            self.transitionAlpha += constants.TRANSITION_SPEED
            self.transitionPos -= constants.SCREEN_SIZE[1] / (155 / constants.TRANSITION_SPEED)

            if self.transitionAlpha >= 255:
                self.transitionPos = -constants.SCREEN_SIZE[1]
                self.transitionAlpha = 255
                return True
        
        return False
    

    # Updates the buttons, returning the button pressed
    # Also returns "resume" if the escape button has been pressed
    def update(self, inputs, mousePos, mouseInputs) -> str:
        super().update()

        if self.update_transition():
            return self.transitionSceneTo

        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                return key
        
        if inputs["esc"]:
            self.transition_out("resume")
        
        return "pause"

    
    # Renders buttons, background, and logo to the screen
    def render(self, window):
        super().render()

        # Setting background
        self.background.set_alpha(self.transitionAlpha)
        window.blit(self.background, (0, 0))

        surf = pygame.Surface(constants.SCREEN_SIZE)

        # Rendering buttons
        for button in self.buttons.values():
            button.render(surf)
        
        # Rendering logo centered on the x axis
        surf.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))