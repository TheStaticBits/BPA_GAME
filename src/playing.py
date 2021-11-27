"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import pygame
import os

import src.scene_base
import src.player
import src.ellipse
import src.utility as utility
import src.constants as constants
import src.animation

class Playing(src.scene_base.SceneBase):
    def __init__(self, saveData, tileRenderer):
        super().__init__(__name__)

        self.tileRenderer = tileRenderer

        # Loading levels from levels.txt
        self.levels = utility.load_levels()

        # Setting data based off of save data from save.db
        self.level = int(saveData["level"])
        self.room = int(saveData["room"])

        self.crystals = [int(x) for x in list(saveData["crystals"])] # Converting the saved string to a list of ints

        self.currentCrystal = False # If the crystal in the current level has been collected

        self.remove_collected_crystals() # Removing crystals that are already collected from the levels

        # Loads the tile images from the list in constants.py
        self.load_tiles()

        # Setting up the player based on the save data
        self.setup_player(
            float(saveData["playerX"]), 
            float(saveData["playerY"]),
            float(saveData["playerYVelocity"]),
            float(saveData["playerXVelocity"]),
        )

        self.ellipse = src.ellipse.Ellipse((self.player.rect.y, self.player.rect.x), self.room, self.level)

        # Setting up background tile
        self.background = self.tileKey["w"]["tile"].convert_alpha().copy()
        self.background.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)

        # Setup tile drawing surface
        self.tileSurface = pygame.Surface((
            constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0],
            constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]
        ))
        self.tileRenderer.draw_tiles(self.tileSurface)
        self.tilesChanged = False

        # Loading tile animations
        self.load_tile_anims()
        self.setup_room_tile_anims()

        # Setting up gravity beam animation
        self.gravityBeam = src.animation.Animation(
            constants.GRAV_BEAM_DELAY,
            constants.GRAV_BEAM_PATH, 
            constants.GRAV_BEAM_WIDTH
        )

        # Gravity line pull direction
        # Each entity still has its own pull direction for if it's below or above the line.
        # 1 is normal gravity (pull towards the line)
        # -1 is reverse gravity (pull away from the line)
        self.gravityDir = 1

        # EDITOR CONTROLS:
        self.placeTile = "c" # Tile to be placed when you click


    def remove_collected_crystals(self):
        # This is just an amazing tower of for and if statements.
        # It basically goes through and removes all crystals that have already been collected.
        for levelNum, collected in enumerate(self.crystals):
            if collected:
                for roomNum, room in enumerate(self.levels[levelNum]):
                    for y, row in enumerate(room):
                        for x, tile in enumerate(row):
                            if tile == "c":
                                self.levels[levelNum][roomNum][y][x] = " "


    def reset_crystal_in_level(self):
        self.levels[self.level] = utility.load_levels()[self.level]


    # Sets up the player, given a position or using the level to find the starting position
    def setup_player(
        self, 
        playerX = -1, 
        playerY = -1,
        yVelocity = 0,
        xVelocity = 0
        ):

        # If there was no data passed in, set the position to the tile "p" in the level
        if playerX == -1 and playerY == -1:
            playerStart = (0, 0)

            # Iterating through the rows in the room
            for y, row in enumerate(self.levels[self.level][self.room]):
                # Iterating through the individual letters in the row
                for x, tile in enumerate(row):
                    if tile == "p":
                        # Setting the player's starting based on the position of the "p" tile
                        playerStart = (
                            x * constants.TILE_SIZE[0],
                            y * constants.TILE_SIZE[1]
                        )

        else: # If there was a position supplied
            playerStart = (playerX, playerY) # Setting the player's start to the given position

        self.player = src.player.Player(playerStart, yVelocity, xVelocity) # Creating the player object based on the position found/given


    def update(
        self, 
        inputs, # Dictionary of keys pressed
        mousePos, # Position of the mouse
        mousePressed # Which mouse buttons were pressed
        ):
        super().update()

        """
        Updating Player
        """
        playerState = self.player.update(self.levels[self.level][self.room], inputs, self.gravityDir) # Updating the player with the inputs

        # If the player moved to the far right of the screen
        if playerState == "right":
            self.room += 1
            
            # If the room number has hit the end of the level
            if self.room >= len(self.levels[self.level]):
                if self.currentCrystal:
                    self.crystals[self.level] = 1
                    self.currentCrystal = False
                
                # Resetting the room number and incrementing the level number
                self.room = 0
                self.level += 1
                
                # Resetting the player
                self.setup_player()
            
            else:
                self.player.rect.x -= (constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0]) - constants.PLAYER_WIDTH) # Moving the player to the complete other side of the room

            self.tilesChanged = True # This will make the renderer rerender the tiles in the render function

        # If the player moved to the far left of the screen
        elif playerState == "left":
            if self.room > 0: # If it isn't the start of a level
                self.room -= 1

                self.player.rect.x += constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0]) - constants.PLAYER_WIDTH # Moving the player to the opposite side of the screen

                self.tilesChanged = True # Rerendering the tiles

        # If the player died
        elif playerState == "dead":
            self.room = 0 # Resetting the room number
            self.setup_player() # Resetting the player
            self.tilesChanged = True # Rerendering the tiles
            self.gravityDir = 1 # Resetting gravity

            # Resetting crystal
            if self.currentCrystal:
                self.reset_crystal_in_level()
                self.currentCrystal = False
        
        # If the return result was of a tile
        # Play the "struck" animation for the tile
        elif playerState != "alive":
            if self.tileRenderer.change_tile_anim(playerState[1], "struck"):
                if playerState[0] == "g": # Gravity orb
                    self.gravityDir *= -1 # Changing the gravity direction
                
                elif playerState[0] == "c":
                    self.levels[self.level][self.room][playerState[1][1]][playerState[1][0]] = " " # Removing the tile

                    if not self.crystals[self.level]:
                        self.currentCrystal = True
        
        # Gravity beam animation update
        self.gravityBeam.update()

        # Ellipse update
        self.ellipse.update(self.room, self.level, self.levels[self.level][self.room], self.gravityDir)

        self.tileRenderer.update_tile_anims()


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
            utility.save_room(self.level, self.room, self.levels[self.level][self.room]) # Saves the room to the levels.txt file


    # Renders everything to the screen
    def render(self, window):
        super().render()

        if self.tilesChanged: # If the tiles have changed, rerender them
            self.tileSurface.fill((0, 0, 0))
            self.tileRenderer.draw_tiles(self.levels, self.level, self.room, self.tileSurface)
            
            self.tilesChanged = False

            self.tileRenderer.setup_room_tile_anims(self.levels, self.level, self.room)
        
        # Drawing tiles
        window.blit(self.tileSurface, (0, 0))

        # Drawing tiles with animations
        self.render_tiles_with_anims(window)

        # Drawing gravity beam
        for x in range(
            (constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0]) 
            // constants.GRAV_BEAM_WIDTH
            ): # Goes through the center of the screen

            # Draws the gravity beam
            self.gravityBeam.render(
                window, 
                (x * constants.GRAV_BEAM_WIDTH, 
                (constants.GRAV_BEAM_TILE_Y_POS * constants.TILE_SIZE[1]) - (self.gravityBeam.images[0].get_height() / 2)) # Centers the beam
            )

        # Drawing Ellipse
        self.ellipse.render(self.room, self.level, window)

        # Drawing player
        self.player.render(window)