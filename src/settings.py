import pygame
import logging

import src.constants as constants
import src.utility as utility
import src.tile_renderer
import src.button

class Settings:
    """Handles the settings menu, the options, and everything within it"""
    def __init__(self, save):
        """Initiates buttons, backgrounds, and other things"""
        self.logger = logging.getLogger(__name__)
        
        # For audio slider
        self.volume = int(save["volume"])

        # Getting background level data
        menuLevel, menuLevelData = utility.load_levels(constants.MAIN_MENU_LEVEL_PATH)
        self.music = menuLevelData[1]["music"]

        # Font objects for rendering text
        self.font = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE)
        self.largeFont = pygame.font.Font(constants.FONT_PATH, 45)

        # Creating background image
        self.bg = pygame.Surface(constants.SCREEN_SIZE)
        tr = src.tile_renderer.TileRenderer()
        tr.draw_tiles(
            menuLevel[1][0], 0,
            self.bg, menuLevelData[1]["background"]
        )
        # Screen shadow
        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH)
        # Back image
        back = pygame.image.load(constants.BACK_PATH)
        
        arrow = pygame.image.load(constants.ARROW_PATH)

        # Creating buttons
        # Button layout
        buttons = {
            # Check box settings
            "showText": ("check", 150, constants.SCREEN_SIZE[1] / 2 - 24),
            "showCharacters": ("check", 150, constants.SCREEN_SIZE[1] / 2),
            "showFPS": ("check", 150, constants.SCREEN_SIZE[1] / 2 + 24),

            # Audio level buttons on the left
            "volumeUp": (pygame.transform.rotate(arrow, 90), 100, constants.SCREEN_SIZE[1] / 2 - 5),
            "volumeDown": (pygame.transform.rotate(arrow, 270), 100, constants.SCREEN_SIZE[1] / 2 + 35),

            "back": (back, 32 + back.get_width() / 2, constants.SCREEN_SIZE[1] / 2 - back.get_height() / 2)
        }

        self.buttons = {}
        # Creating actual button objects from the button data
        for name, data in buttons.items():
            if data[0] == "check":
                # Check button
                self.buttons[name] = src.button.Button(
                    data[1], data[2],
                    imagePath = constants.CHECK_BOX_PATH,
                    toggle = True, 
                    toggledImgPath = constants.CHECK_MARK_PATH
                )
                
                # Updating check box to match the save
                self.buttons[name].toggled = int(save[name])

            else:
                # Button with image
                self.buttons[name] = src.button.Button(
                    data[1], data[2],
                    image = data[0]
                )
    

    def update(self, mousePos, mouseInputs):
        """Updates buttons and returns a string if a button was pressed"""

        for name, button in self.buttons.items():
            if button.update(mousePos, mouseInputs):
                if name == "volumeUp": # Pressed volume up button
                    # Increasing the volume
                    self.volume += 5
                    if self.volume > 100: # Locking to 100 if above
                        self.volume = 100
                    self.logger.info(f"Audio level is now {self.volume}")
                    # Setting volume
                    pygame.mixer.music.set_volume(self.volume / 100)
                elif name == "volumeDown": # Pressed volume down button
                    # Decreasing volume level by 5
                    self.volume -= 5
                    if self.volume < 0: # Locking to zero if below it
                        self.volume = 0
                    self.logger.info(f"Audio level is now {self.volume}")
                    # Setting volume
                    pygame.mixer.music.set_volume(self.volume / 100)
                
                else:
                    return name
    

    def render(self, window):
        """Renders everything in the settings menu to the screen"""
        window.blit(self.bg, (0, 0))
        window.blit(self.screenShadow, (0, 0))

        for button in self.buttons.values():
            button.render(window)

        # Settings title
        utility.centered_text(window, "Settings", (constants.SCREEN_SIZE[0] / 2, 30), self.largeFont)
        
        # Check box text for showText button
        utility.render_text(window, "Show Tutorial Text", (160, constants.SCREEN_SIZE[1] / 2 - 26), self.font)
        # Check box text for showCharacters button
        utility.render_text(window, "Show Ellipse and Corlen", (160, constants.SCREEN_SIZE[1] / 2 - 2), self.font)
        # Check box text for showFPS button
        utility.render_text(window, "Show FPS Counter", (160, constants.SCREEN_SIZE[1] / 2 + 22), self.font)

        # Render the audio text
        utility.centered_text(window, "Music\nVolume", (100, constants.SCREEN_SIZE[1] / 2 - 35), self.font)
        # Render the audio level
        utility.centered_text(window, f"{self.volume}%", (100, constants.SCREEN_SIZE[1] / 2 + 15), self.font)