"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import pygame
import math

import src.base_level
import src.tile_renderer
import src.utility as utility
import src.constants as constants

"""
This class, Playing, handles everything that goes on
within normal levels. It uses things from the BaseLevel class
which are also used by the boss level handler.
"""
class Playing(src.base_level.BaseLevel):
    def __init__(self): # Initializes all
        super().__init__(__name__)

        self.font = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE) # Setting up the font
        self.get_text() # Getting the text for the current room
        
        # Setup tile drawing surface
        self.tileSurface = pygame.Surface(constants.SCREEN_SIZE)

        self.tileRenderer = src.tile_renderer.TileRenderer()
        
        self.load_room() # Drawing the tiles onto the tile surface

        # EDITOR CONTROLS:
        self.placeTile = "w" # Tile to be placed when you click
    
    
    # Calls a bunch of other functions which sets up the world with all the aspects of it
    def setup(self, level, crystals, crystalIndex):
        self.logger.info(f"Setting up level {level}")

        self.level = level

        super().reset_crystal(level)
        if "crystal moves on" not in self.levelData[level]: # If the crystal isn't required for the level
            if crystals[crystalIndex]: 
                super().remove_crystal(level)
        
        super().reset_all()
        self.get_text()
        self.load_room()
    
    
    # Restarts the level the player is in
    def restart_level(self):
        self.logger.info("Restarting")

        # If the player has previously collected a crystal, it will be reset
        if self.currentCrystal: super().reset_crystal(self.level)
        
        super().reset_all()
        self.get_text()
        self.load_room()
        

    # Loads the rendered tiles in the room,
    # while also setting up the animated tiles in the tile renderer
    def load_room(self):
        self.logger.info("Loading tiles in room")
        
        self.get_text()
        # This is done so that the tile renderer doesn't have to rerender tiles every frame
        # (for performance)
        # Instead, the tiles on screen are saved and rendered from that
        self.tileSurface.fill(constants.BLACK)
        self.tileRenderer.draw_tiles(
            self.levels[self.level][self.room], self.room,
            self.tileSurface, 
            self.levelData[self.level]["background"]
        )
        self.tileRenderer.setup_room_tile_anims(self.levels[self.level][self.room])
    
    
    # Sets up the text in the room if there is any given in the level data
    def get_text(self):
        self.text = None
        self.textWavX = 0

        if f"text {self.room}" in self.levelData[self.level]:
            self.text = self.levelData[self.level][f"text {self.room}"]


    # Updates the player
    def update(self, window):
        inputs = window.inputs # Dictionary of keys pressed
        mousePos = window.mousePos # Position of the mouse
        mousePressed = window.mousePressed # Which mouse buttons were pressed

        result = super().update(
            inputs,
            self.tileRenderer
        )

        if result == "right":
            if self.room == 0: # If it switched to a new level
                return self.level
        
        if result in ("right", "left"): # If the player moved to a new room in the level
            self.load_room()
        
        elif result == "dead":
            self.restart_level()
            super().popup("You Died!")
        
        elif result == "crystal" or result == "crystal mid-level":
            return result

        # Updates all tiles that have animations (such as orbs)
        self.tileRenderer.update_tiles_with_anims()

        if constants.LEVEL_EDITING:
            """  Mouse Inputs for Editor  """
            # The position of the tile that the mouse is hovering over
            tilePos = (
                mousePos[0] // constants.TILE_SIZE[0],
                mousePos[1] // constants.TILE_SIZE[1]
            )

            if mousePressed["left"]: # If left clicked
                if self.levels[self.level][self.room][tilePos[1]][tilePos[0]] != self.placeTile:
                    # Sets the tile the mouse is hovering over to the placeTile
                    self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = self.placeTile # placeTile is the tile to be placed
                    self.load_room()
            
            if mousePressed["center"]: # If center clicked
                self.placeTile = self.levels[self.level][self.room][tilePos[1]][tilePos[0]] # Changing the placeTile to the one the mouse is hovering over

            if mousePressed["right"]: # If right clicked
                if self.levels[self.level][self.room][tilePos[1]][tilePos[0]] != " ":
                    # Sets the tile the mouse is hovering over to air
                    self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "
                    self.load_room()
            
            if inputs["space"]:
                self.logger.info("Saving room")
                utility.save_room(self.level, self.room, self.levels[self.level][self.room], constants.LEVELS_PATH) # Saves the room to the levels.txt file


    # Renders everything to the screen
    def render(self, window):        
        # Drawing tiles
        window.blit(self.tileSurface, (0, 0))

        # Drawing tiles with animations
        self.tileRenderer.render_tiles_with_anims(window, self.gravityDir, self.gravBeamYPos)

        # Renders entities and gravity beam
        super().render(window)
        super().render_grav_beam(window)
        
        # Drawing text if there is any in the room
        if self.text is not None:
            self.textWavX += 0.05
            
            tList = self.text.split("\\n")

            # Iterating through a list of the text rows,
            # rendering for every row
            for count, text in enumerate(tList):
                # Getting the surface with text on it
                if text != "":
                    renderText = self.font.render(text, False, constants.WHITE)

                    position = (
                        constants.SCREEN_SIZE[0] / 2 - renderText.get_width() / 2, # Centering text on screen 
                        20 + math.sin(self.textWavX) * 5 + count * 12
                    )

                    utility.draw_text_with_border(window, position, text, self.font, constants.WHITE, renderText = renderText)
        
        super().render_screen_shadow(window)
        super().render_popup(window)