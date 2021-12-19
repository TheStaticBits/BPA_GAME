import pygame

import src.button
import src.constants as constants
import src.scene_base

class PauseMenu(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        font = pygame.font.Font(constants.FONT_PATH, 25)
        self.logo = pygame.image.load(constants.LOGO_PATH).convert_alpha()

        buttons = {
            "resume": (120, "Resume"),
            "restart": (150, "Restart Level"),
            "mainMenu": (180, "Main Menu")
        }

        self.buttons = {}
        for name, values in buttons.items():
            self.buttons[name] = src.button.Button(
                constants.SCREEN_SIZE[0] / 2,
                values[0],
                fontObj = font,
                text = "Resume",
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

        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                return key
            
            elif key == "resume":
                if inputs["esc"]:
                    return "resume"
        
        return "pause"

    def render(self, window):
        super().render()

        window.blit(self.background, (0, 0))

        for button in self.buttons.values():
            button.render(window)
        
        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 20))