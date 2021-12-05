import pygame

import src.scene_base
import src.constants as constants
import src.button

class MainMenu(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        fontObj = pygame.font.Font(constants.FONT_PATH, 30)

        self.playButton = src.button.Button(
            constants.SCREEN_SIZE[0] / 2,
            constants.SCREEN_SIZE[1] / 2,
            fontObj,
            "Continue"
        )


    def update(self, mousePos, mouseInputs):
        super().update()

        if self.playButton.update(mousePos, mouseInputs):
            return "start"

    
    def render(self, window):
        super().render()

        self.playButton.render(window)