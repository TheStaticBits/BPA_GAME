import pygame

import src.scene_base
import src.constants as constants
import src.utility as utility
import src.button
import src.tile_renderer

class MainMenu(src.scene_base.SceneBase):
    def __init__(self, save, levelsList, levelsCompleted):
        super().__init__(__name__)

        self.levelsList = levelsList
        self.levelsCompleted = levelsCompleted
        self.lvlsIndex = int(save["level"])

        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        self.logo = pygame.image.load(constants.LOGO_PATH).convert_alpha()

        self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)

        mainMenuLevel, mainMenuLevelData = utility.load_levels(constants.MAIN_MENU_LEVEL_PATH)

        tileRenderer = src.tile_renderer.TileRenderer()
        self.background = pygame.Surface(constants.SCREEN_SIZE)
        tileRenderer.draw_tiles(
            mainMenuLevel[0][0],
            self.background,
            mainMenuLevelData[0]["background"],
        )

        self.music = mainMenuLevelData[0]["music"]

        buttons = {
            "start": (120, constants.SCREEN_SIZE[1] / 2, "Continue"),
            "newSave": (120, constants.SCREEN_SIZE[1] / 2 + 30, "Restart"), 
            "help": (120, constants.SCREEN_SIZE[1] / 2 + 60, "Help"), 
            "left": (210, constants.SCREEN_SIZE[1] / 2 + 25, "<"), 
            "right": (300, constants.SCREEN_SIZE[1] / 2 + 25, ">"),
            "play": (255, constants.SCREEN_SIZE[1] / 2 + 60, "Play"),
        }

        fontObj = pygame.font.Font(constants.FONT_PATH, 30)
        self.buttons = {}
        for key, value in buttons.items():
            self.buttons[key] = src.button.Button(
                value[0],
                value[1],
                fontObj,
                value[2],
                textOffset = 2
            )

        self.otherTextFont = pygame.font.Font(constants.FONT_PATH, 15)


    def start_music(self):
        utility.play_music(self.music)


    def update_info(self, level, levelsCompleted):
        self.lvlsIndex = level
        self.levelsCompleted = levelsCompleted
    

    def get_status(self, level):
        if self.levelsCompleted[level] == 1:
            return "Completed", constants.GREEN
        elif level == 0 or self.levelsCompleted[level - 1] == 1:
            return "Unlocked", constants.YELLOW
        else: 
            return "Locked", constants.RED


    def update(self, mousePos, mouseInputs):
        super().update()

        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                if key == "left":
                    self.lvlsIndex -= 1
                    if self.lvlsIndex < 0:
                        self.lvlsIndex = len(self.levelsList) - 1
                
                elif key == "right":
                    self.lvlsIndex += 1
                    if self.lvlsIndex >= len(self.levelsList):
                        self.lvlsIndex = 0
                    
                elif key == "play":
                    if self.get_status(self.lvlsIndex)[0] != "Locked":
                        return "play"

                else:
                    return key


    def render_text(self, window, text, position, color = constants.WHITE):
        surf = self.otherTextFont.render(text, False, color)
        window.blit(surf, (position[0] - surf.get_width() / 2, position[1]))

    
    def render(self, window):
        super().render()
        
        window.blit(self.background, (0, 0))
        window.blit(self.screenShadow, (0, 0))

        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))

        for button in self.buttons.values():
            button.render(window)
        
        self.render_text(window, "Level Picker", (255, constants.SCREEN_SIZE[1] / 2 + 5))
        self.render_text(window, f"Level: {self.lvlsIndex + 1}", (255, constants.SCREEN_SIZE[1] / 2 + 20))
        self.render_text(window, self.levelsList[self.lvlsIndex], (255, constants.SCREEN_SIZE[1] / 2 + 30))

        levelStatus, color = self.get_status(self.lvlsIndex)
        
        self.render_text(window, levelStatus, (255, constants.SCREEN_SIZE[1] / 2 + 45), color)