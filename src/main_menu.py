import pygame

import src.scene_base
import src.constants as constants
import src.utility as utility
import src.button
import src.tile_renderer

"""
Handles the buttons on the main menu, rendering of main menu, 
and also the level selector on the main menu.
"""
class MainMenu(src.scene_base.SceneBase):
    # Sets up variables to default and loading images used on the menu
    def __init__(self, save, levelsList, levelsCompleted, crystals, remove_cutscenes):
        super().__init__(__name__) # Logging

        self.levelsList = levelsList
        self.levelsCompleted = levelsCompleted
        self.crystals = crystals
        # Function which takes a level number and removes the cutscenes from it
        self.remove_cutscenes = remove_cutscenes
        self.lvlsIndex = int(save["level"]) # For level selector

        self.ending = int(save["unlockedEnding"])

        self.crystal_check = pygame.image.load(constants.CRYSTAL_CHECK_PATH).convert_alpha()
        self.crystal_x = pygame.image.load(constants.CRYSTAL_X_PATH).convert_alpha()

        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        self.logo = pygame.image.load(constants.TIN_LOGO_PATH).convert_alpha()

        self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)

        mainMenuLevel, mainMenuLevelData = utility.load_levels(constants.MAIN_MENU_LEVEL_PATH)

        # Getting the background surface, drawing it once on a Pygame Surface
        tileRenderer = src.tile_renderer.TileRenderer()
        self.background = pygame.Surface(constants.SCREEN_SIZE)
        tileRenderer.draw_tiles(
            mainMenuLevel[0][0], 0,
            self.background, # Surface
            mainMenuLevelData[0]["background"], # Background tile
        )

        self.music = mainMenuLevelData[0]["music"]

        # Buttons teplate
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
                value[0], # x
                value[1], # y
                fontObj = fontObj,
                text = value[2],
                textOffset = 2
            )

        # For nonbutton text
        self.otherTextFont = pygame.font.Font(constants.FONT_PATH, 15)


    # Plays music
    def start_music(self):
        utility.play_music(self.music)


    # Updates information given data
    def update_info(self, level, levelsCompleted, crystals):
        self.lvlsIndex = level
        self.levelsCompleted = levelsCompleted
        self.crystals = crystals
    

    # Looks inside the levelsCompleted variable and returns a tuple
    # (level completed or not, rga value) 
    def get_status(self, level):
        if self.levelsCompleted[level] == 1:
            return "Completed", constants.GREEN
        # If the level before this one was completed
        elif level == 0 or self.levelsCompleted[level - 1] == 1:
            return "Unlocked", constants.YELLOW
        else: 
            return "Locked", constants.RED


    # Updates buttons, returning a string for the result of which button was pressed
    def update(self, mousePos, mouseInputs):
        super().update()

        # Iterating through all buttons
        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs): # If the button was pressed
                # Finds the last normal level's id
                last_normal_level = max(
                    utility.find_last_item(self.levelsList, "Boss Level"), 
                    utility.find_last_item(self.levelsList, "Normal Level")
                )
                
                if key == "left": # If the button was the left arrow in the level selector
                    # If the level displayed is one of the endings, set it to the last non-ending level
                    if self.lvlsIndex > last_normal_level:
                        self.lvlsIndex = last_normal_level
                    else:
                        self.lvlsIndex -= 1
                        # If it went below zero
                        if self.lvlsIndex < 0:
                            if self.ending == -1: # If the player has not gotten to an ending
                                # setting it to the last level that is not an ending
                                self.lvlsIndex = last_normal_level
                            else:
                                # Setting it to the ending the player got
                                self.lvlsIndex = last_normal_level + self.ending
                
                elif key == "right": # if the button pressed was the right arrow
                    # If the level selected at the time was an ending, set it to the first level
                    if self.lvlsIndex > last_normal_level:
                        self.lvlsIndex = 0
                    else:
                        self.lvlsIndex += 1
                        # If the new level is an ending
                        if self.lvlsIndex > last_normal_level:
                            if self.ending == -1: # If the player hasn't gotten an ending
                                self.lvlsIndex = 0 # Setting to first level
                            else:
                                # Setting to the ending the player got
                                self.lvlsIndex = last_normal_level + self.ending
                    
                elif key == "play":
                    if self.get_status(self.lvlsIndex)[0] != "Locked":
                        return "play"

                else:
                    return key


    # Renders text centered on the x position
    def render_text(self, window, text, position, color = constants.WHITE):
        surf = self.otherTextFont.render(text, False, color) # Rendering to a surface
        window.blit(surf, (position[0] - surf.get_width() / 2, position[1])) # Centered

    
    # Renders everything in the scene to the window
    def render(self, window):
        super().render()
        
        window.blit(self.background, (0, 0))
        window.blit(self.screenShadow, (0, 0))

        # Centers logo on the x axis
        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))

        # Rendering all buttons
        for button in self.buttons.values():
            button.render(window)
        
        # Draws the "level selector" text
        self.render_text(window, "Level Selector", (255, constants.SCREEN_SIZE[1] / 2 + 5))
        

        if self.levelsList[self.lvlsIndex] != "Cutscene": # If the selected level isn't a cutscene
            # Level number not including cutscenes (and adding one so it doesn't start at zero)
            text = f"Level: {self.remove_cutscenes(self.lvlsIndex) + 1}"
        else:
            # Getting cutscene name
            text = self.levelData[self.lvlsIndex]["cutscene"]
        self.render_text(window, text, (255, constants.SCREEN_SIZE[1] / 2 + 20))

        # Rendering the type of level
        self.render_text(window, self.levelsList[self.lvlsIndex], (255, constants.SCREEN_SIZE[1] / 2 + 30))

        levelStatus, color = self.get_status(self.lvlsIndex)
        
        # Rendering the status of the level, whether it's completed, unlocked, or locked
        self.render_text(window, levelStatus, (255, constants.SCREEN_SIZE[1] / 2 + 45), color)

        # If the level isn't a cutscene
        if "cutscene" not in self.levelData[self.lvlsIndex]and "crystal moves on" not in self.levelData[self.lvlsIndex]:
            # Rendering the little crystal icon for whether you've gotten it or not
            if self.crystals[self.remove_cutscenes(self.lvlsIndex)]:
                window.blit(self.crystal_check, (218, constants.SCREEN_SIZE[1] / 2 + 22))
            else:
                window.blit(self.crystal_x, (218, constants.SCREEN_SIZE[1] / 2 + 22))