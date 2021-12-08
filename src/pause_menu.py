import pygame

import src.button
import src.constants as constants
import src.scene_base

class PauseMenu(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        font = pygame.font.Font(constants.FONT_PATH, 25)

        self.resumeButton = src.button.Button(
            constants.SCREEN_SIZE[0] / 2,
            100,
            font,
            "Resume",
            textOffset = 2
        )

        self.mainMenuButton = src.button.Button(
            constants.SCREEN_SIZE[0] / 2,
            140,
            font,
            "Main Menu",
            textOffset = 2
        )

        self.background = None
    

    def check_for_pause(self, scene, inputs) -> bool:
        return inputs["esc"] and scene in ("playing", "bossLevel", "cutscene")

    
    def update_background(self, background):
        self.background = background.copy()
        self.background.set_alpha(100)
    

    def update(self, inputs, mousePos, mouseInputs) -> str:
        super().update()

        if self.resumeButton.update(mousePos, mouseInputs) or inputs["esc"]:
            return "resume"

        elif self.mainMenuButton.update(mousePos, mouseInputs):
            return "mainMenu"
        
        return "pause"

    def render(self, window):
        super().render()

        window.blit(self.background, (0, 0))

        self.resumeButton.render(window)
        self.mainMenuButton.render(window)