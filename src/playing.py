"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import pygame
import math

import src.scene_base
import src.base_level
import src.tile_renderer
import src.utility as utility
import src.constants as constants

class Playing(src.base_level.BaseLevel):
    def __init__(self, saveData):
        super().__init__(saveData, __name__)

        self.font = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE) # Setting up the font
        self.get_text() # Getting the text for the current room
        
        # Setup tile drawing surface
        self.tileSurface = pygame.Surface((
            constants.SCREEN_SIZE[0],
            constants.SCREEN_SIZE[1]
        ))

        self.tileRenderer = src.tile_renderer.TileRenderer()
        
        self.load_room() # Drawing the tiles onto the tile surface

        self.tilesChanged = False

        # EDITOR CONTROLS:
        self.placeTile = "c" # Tile to be placed when you click
    
    
    # Calls a bunch of other functions which sets up the world with all the aspects of it
    def setup(self):
        self.get_text()
        self.load_room()
        self.start_music()
        self.check_entity_rendering()
        self.setup_player()


    def load_room(self):
        self.get_text()
        self.tileSurface.fill((0, 0, 0))
        self.tileRenderer.draw_tiles(
            self.levels[self.level][self.room], 
            self.tileSurface, 
            self.levelData[self.level]["background"]
        )
        self.tileRenderer.setup_room_tile_anims(self.levels[self.level][self.room])
    
    
    def get_text(self):
        self.text = None
        self.textWavX = 0

        try:
            if self.levelData[self.level][f"text {self.room}"] != "":
                self.text = self.levelData[self.level][f"text {self.room}"]
                self.textSurface = self.font.render(self.text, False, (255, 255, 255))
                
                self.fontX = (constants.SCREEN_SIZE[0]) / 2 - self.textSurface.get_width() / 2

        except KeyError: # If that room doesn't have text 
            pass


    def update(
        self, 
        inputs, # Dictionary of keys pressed
        mousePos, # Position of the mouse
        mousePressed # Which mouse buttons were pressed
        ):
        changeToCutscene = super().update(
            inputs,
            self.tileRenderer
        )

        if changeToCutscene == "right":
            if self.room == 0: # If it switched to a new level
                check = self.check_for_boss()
                if check is not None:
                    return ("bossLevel", check) # Switches to the boss

                check = self.check_for_cutscene()
                if check is not None:
                    return ("cutscene", check) # Switches to the cutscene

        self.tileRenderer.update_tiles_with_anims()


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
                self.tilesChanged = True # Sets the tiles to be rerendered, since they changed
        
        if mousePressed["center"]: # If center clicked
            self.placeTile = self.levels[self.level][self.room][tilePos[1]][tilePos[0]] # Changing the placeTile to the one the mouse is hovering over

        if mousePressed["right"]: # If right clicked
            if self.levels[self.level][self.room][tilePos[1]][tilePos[0]] != " ":
                # Sets the tile the mouse is hovering over to air
                self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "
                self.tilesChanged = True # Sets the tiles to be rerendered
        
        # Other editor inputs
        if inputs["space"]:
            utility.save_room(self.level, self.room, self.levels[self.level][self.room], constants.LEVELS_PATH) # Saves the room to the levels.txt file


    # Renders everything to the screen
    def render(self, window):
        if self.tilesChanged: # If the tiles have changed, rerender them
            self.load_room()

            self.tilesChanged = False
        
        # Drawing tiles
        window.blit(self.tileSurface, (0, 0))

        # Drawing tiles with animations
        self.tileRenderer.render_tiles_with_anims(window, self.gravityDir)

        # Renders entities and gravity beam
        super().render(window)
        super().render_grav_beam(window)

        self.textWavX += 0.05
        
        # Drawing text if there is any in the room
        if self.text is not None:
            window.blit(
                self.textSurface, 
                (
                    self.fontX, 
                    50 + math.sin(self.textWavX) * 5
                )
            )
        
        super().render_screen_shadow(window)