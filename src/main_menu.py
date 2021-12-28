import pygame
import logging

import src.constants as constants
import src.utility as utility
import src.button
import src.tile_renderer


class MainMenu():
    """
    Handles the buttons on the main menu, rendering of main menu, 
    and also the level selector on the main menu.
    """
    def __init__(self, save, levelsList, levelsCompleted, crystals, remove_cutscenes):
        """Sets up variables to default and loading images used on the menu"""
        self.logger = logging.getLogger(__name__) # Logging

        self.levelsList = levelsList
        self.levelsCompleted = levelsCompleted
        self.crystals = crystals
        # Function which takes a level number and removes the cutscenes from it
        self.remove_cutscenes = remove_cutscenes
        self.lvlsIndex = int(save["level"]) # For level selector

        self.ending = int(save["unlockedEnding"])

        self.speedrunHighscore = save["speedrunHighscore"]

        self.crystal_check = pygame.image.load(constants.CRYSTAL_CHECK_PATH).convert_alpha()
        self.crystal_x = pygame.image.load(constants.CRYSTAL_X_PATH).convert_alpha()

        arrow = pygame.image.load(constants.ARROW_PATH).convert_alpha()

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
            "speedrun": (120, constants.SCREEN_SIZE[1] / 2 + 60, "Speedrun"), 

            # Flips the left button arrow to face the left
            "left": (210, constants.SCREEN_SIZE[1] / 2 + 25, pygame.transform.flip(arrow, True, False)), 
            "right": (300, constants.SCREEN_SIZE[1] / 2 + 25, arrow),
            "play": (255, constants.SCREEN_SIZE[1] / 2 + 60, "Play"),

            "showText": (345, constants.SCREEN_SIZE[1] / 2 - 50, "check"),
            "showCharacters": (345, constants.SCREEN_SIZE[1] / 2 + 10, "check"),
        }

        # Populating the self.buttons dict with buttons created from the data in the buttons variable
        fontObj = pygame.font.Font(constants.FONT_PATH, 30)
        self.buttons = {}
        for key, value in buttons.items():
            if isinstance(value[2], str) and value[2] != "check":
                # Normal text button
                self.buttons[key] = src.button.Button(
                    value[0], value[1], # x and y
                    fontObj = fontObj,
                    text = value[2],
                    textOffset = 2
                )
            
            elif value[2] == "check":
                # Check button
                self.buttons[key] = src.button.Button(
                    value[0], value[1],
                    imagePath = constants.CHECK_BOX_PATH,
                    toggle = True, 
                    toggledImgPath = constants.CHECK_MARK_PATH
                )
                
                # Updating check box to match the save
                self.buttons[key].toggled = int(save[key])

            else:
                # Image button
                self.buttons[key] = src.button.Button(
                    value[0], value[1],
                    image = value[2]
                )

        # For nonbutton text
        self.otherTextFont = pygame.font.Font(constants.FONT_PATH, 15)


    def start_music(self):
        """Plays main menu music"""
        utility.play_music(self.music)


    def update_info(self, level, levelsCompleted, ending, crystals):
        """Updates information given data"""
        self.lvlsIndex = level
        self.levelsCompleted = levelsCompleted
        self.ending = ending
        self.crystals = crystals
    

    def get_status(self, level) -> tuple:
        """
        Looks inside the levelsCompleted variable and returns a tuple related to the information found. In this form:
        (level completed or not (bool), rga value (tuple))
        """
        if self.levelsCompleted[level] == 1:
            return "Completed", constants.GREEN
        # If the level before this one was completed
        elif level == 0 or self.levelsCompleted[level - 1] == 1:
            return "Unlocked", constants.YELLOW
        else: 
            return "Locked", constants.RED


    def update(self, mousePos, mouseInputs):
        """Updates buttons, returning a string for the result of which button was pressed"""
        # Finds the last normal level's id (for some buttons)
        last_normal_level = max(
            utility.find_last_item(self.levelsList, "Boss Level"), 
            utility.find_last_item(self.levelsList, "Normal Level")
        )

        # Iterating through all buttons
        for key, button in self.buttons.items():
            if button.update(mousePos, mouseInputs): # If the button was pressed
                self.logger.info(f"{key} button pressed")
                
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
                    
                elif key == "play": # Play button
                    if self.get_status(self.lvlsIndex)[0] != "Locked":
                        return key
                
                elif key == "speedrun":
                    # Only allows you to enter this mode if you've reached an ending
                    if self.ending != -1:
                        return key

                else:
                    return key


    def render_text(self, window, text, position, color = constants.WHITE):
        """Renders text centered on the x position. Also accounts for newlines."""
        text = text.split("\n")
        for count, txt in enumerate(text):
            surf = self.otherTextFont.render(txt, False, color) # Rendering to a surface
            window.blit(surf, (position[0] - surf.get_width() / 2, position[1] + count * 12)) # Centered

    
    def render(self, window):
        """Renders everything in the scene to the window"""
        window.blit(self.background, (0, 0))
        window.blit(self.screenShadow, (0, 0))

        # Centers logo on the x axis
        window.blit(self.logo, (constants.SCREEN_SIZE[0] / 2 - self.logo.get_width() / 2, 15))

        # Rendering all buttons
        for button in self.buttons.values():
            button.render(window)
        
        # If the mouse is hovering over the Speedrun button, display some infromation underneath
        if self.buttons["speedrun"].selected:
            if self.ending != -1:
                # Displaying highscore
                highscore = utility.seconds_to_readable_time(float(self.speedrunHighscore))
                self.render_text(window, "Highscore: " + highscore, (120, constants.SCREEN_SIZE[1] / 2 + 83))
            else:
                self.render_text(window, "Locked!", (120, constants.SCREEN_SIZE[1] / 2 + 83))
        
        # If the mouse is hovering over the Restart button, say that it wipes your data
        if self.buttons["newSave"].selected:
            self.render_text(window, "IRREVERSIBLE!", (120, constants.SCREEN_SIZE[1] / 2 + 53))

        # Check box text for showText button
        self.render_text(window, "Show\nTutorial\nText", (345, constants.SCREEN_SIZE[1] / 2 - 40))
        # Check box text for showText button
        self.render_text(window, "Show\nEllipse\nand\nCorlen", (345, constants.SCREEN_SIZE[1] / 2 + 20))
        
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