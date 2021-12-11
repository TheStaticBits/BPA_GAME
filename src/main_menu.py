import pygame

import src.scene_base
import src.constants as constants
import src.utility as utility
import src.button
import src.tile_renderer

class MainMenu(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        self.logo = pygame.image.load(constants.LOGO_PATH).convert_alpha()

        levels, levelData = utility.load_levels(constants.MAIN_MENU_LEVEL_PATH)

        tileRenderer = src.tile_renderer.TileRenderer()
        self.background = pygame.Surface(constants.SCREEN_SIZE)
        tileRenderer.draw_tiles(
            levels[0][0],
            self.background,
            levelData[0]["background"],
        )

        self.music = levelData[0]["music"]

        fontObj = pygame.font.Font(constants.FONT_PATH, 30)

        self.buttons = {
            "start": src.button.Button(
                120,
                constants.SCREEN_SIZE[1] / 2,
                fontObj,
                "Continue",
                textOffset = 2
            ),

            "newSave": src.button.Button(
                120,
                constants.SCREEN_SIZE[1] / 2 + 30,
                fontObj,
                "Restart",
                textOffset = 2
            ),
            
            "help": src.button.Button(
                120,
                constants.SCREEN_SIZE[1] / 2 + 60,
                fontObj,
                "Help",
                textOffset = 2
            ),
        }


    def start_music(self):
        utility.play_music(self.music)


    def update(self, mousePos, mouseInputs):
        super().update()

        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                return key

    
    def render(self, window):
        super().render()
        
        window.blit(self.background, (0, 0))
        window.blit(self.screenShadow, (0, 0))

        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))

        for button in self.buttons.values():
            button.render(window)