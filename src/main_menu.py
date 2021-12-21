import pygame
import os

import src.scene_base
import src.constants as constants
import src.utility as utility
import src.button
import src.tile_renderer

class MainMenu(src.scene_base.SceneBase):
    def __init__(self, save, levelsList, levelsCompleted, crystals, remove_cutscenes):
        super().__init__(__name__)

        self.levelsList = levelsList
        self.levelsCompleted = levelsCompleted
        self.crystals = crystals
        self.remove_cutscenes = remove_cutscenes # Function to remove cutscenes from a number
        self.lvlsIndex = int(save["level"])

        self.ending = int(save["unlockedEnding"])

        self.crystal_check = pygame.image.load(constants.CRYSTAL_CHECK_PATH).convert_alpha()
        self.crystal_x = pygame.image.load(constants.CRYSTAL_X_PATH).convert_alpha()

        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        self.logo = pygame.image.load(constants.TIN_LOGO_PATH).convert_alpha()

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

        # Populating the self.buttons dict with buttons created from the data in the buttons variable
        fontObj = pygame.font.Font(constants.FONT_PATH, 30)
        self.buttons = {}
        for key, value in buttons.items():
            self.buttons[key] = src.button.Button(
                value[0],
                value[1],
                fontObj = fontObj,
                text = value[2],
                textOffset = 2
            )

        self.otherTextFont = pygame.font.Font(constants.FONT_PATH, 15)


    def start_music(self):
        utility.play_music(self.music)


    def update_info(self, level, levelsCompleted, crystals):
        self.lvlsIndex = level
        self.levelsCompleted = levelsCompleted
        self.crystals = crystals
    

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
                    if self.lvlsIndex == len(self.levelsList) - 1 - self.ending:
                        self.lvlsIndex = len(self.levelsList) - 1 - constants.AMOUNT_OF_ENDINGS
                    else:
                        self.lvlsIndex -= 1
                        if self.lvlsIndex < 0:
                            if self.ending == -1:
                                self.lvlsIndex = len(self.levelsList) - 1 - constants.AMOUNT_OF_ENDINGS
                            else:
                                self.lvlsIndex = len(self.levelsList) - 1 - self.ending
                
                elif key == "right":
                    if self.lvlsIndex == len(self.levelsList) - 1 - self.ending:
                        self.lvlsIndex = 0
                    else:
                        self.lvlsIndex += 1
                        if self.lvlsIndex >= len(self.levelsList) - constants.AMOUNT_OF_ENDINGS:
                            if self.ending == -1:
                                self.lvlsIndex = 0
                            else:
                                self.lvlsIndex = len(self.levelsList) - 1 - self.ending
                    
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
        
        self.render_text(window, "Level Selector", (255, constants.SCREEN_SIZE[1] / 2 + 5))
        

        if self.levelsList[self.lvlsIndex] != "Cutscene":
            text = f"Level: {self.remove_cutscenes(self.lvlsIndex) + 1}"
        else:
            text = self.levelData[self.lvlsIndex]["cutscene"]

        self.render_text(window, text, (255, constants.SCREEN_SIZE[1] / 2 + 20))    
        self.render_text(window, self.levelsList[self.lvlsIndex], (255, constants.SCREEN_SIZE[1] / 2 + 30))

        levelStatus, color = self.get_status(self.lvlsIndex)
        
        self.render_text(window, levelStatus, (255, constants.SCREEN_SIZE[1] / 2 + 45), color)

        if "cutscene" not in self.levelData[self.lvlsIndex]:
            if self.crystals[self.remove_cutscenes(self.lvlsIndex)]:
                window.blit(self.crystal_check, (218, constants.SCREEN_SIZE[1] / 2 + 22))
            else:
                window.blit(self.crystal_x, (218, constants.SCREEN_SIZE[1] / 2 + 22))