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
    def __init__(self, saveData):
        super().__init__(__name__)

        # Loading levels from levels.txt
        self.levels = utility.load_levels()

        # Setting level and room based off of save data from save.db
        self.level = int(saveData["level"])
        self.room = int(saveData["room"])

        # Loads the tile images from the list in constants.py
        self.load_tiles()

        # Setting up the player based on the save data
        self.setup_player(
            saveData["playerX"], 
            saveData["playerY"],
            saveData["playerVelocity"]
        )

        self.ellipse = src.ellipse.Ellipse((self.player.rect.y, self.player.rect.x), self.room, self.level)

        # Setting up background tile
        self.background = self.tileKey["w"]["tile"].convert_alpha().copy()
        self.background.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)

        # Loading spike tile
        self.spikeTile = pygame.image.load("res/misc/spike.png").convert_alpha()

        # If the tile being checked is on the screen and transparent, used when drawing edges to the screen
        self.check_tile = lambda room, x, y: utility.check_between((x, y), (0, 0), constants.SCREEN_TILE_SIZE) and room[y][x] in constants.TRANSPARENT_TILES 

        # Setup tile drawing surface
        self.tileSurface = pygame.Surface((
            constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0],
            constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]
        ))
        self.draw_tiles(self.tileSurface)
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

        # EDITOR CONTROLS:
        self.placeTile = "j" # Tile to be placed when you click


    def load_tiles(self):
        # Creating a dictionary
        # Keys are the letter used to represent the tile
        self.tileKey = {}

        for tileKey in constants.TILE_KEYS:
            # Setting the key to another dictionary with the individual parts of the tile image
            self.tileKey[tileKey] = {
                "tile": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/tile.png").convert_alpha(),
                "corner": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/corner.png").convert_alpha(),
                "edge": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/edge.png").convert_alpha(),
            }

            if os.path.isfile(f"res/tiles/{constants.TILE_KEYS[tileKey]}/inverse_corner.png"): # If there is an inverse_corner image for the tile
                self.tileKey[tileKey]["inverse_corner"] = pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/inverse_corner.png").convert_alpha() # Load the inverse corner
            
            else: # If there isn't an inverse_corner needed
                self.tileKey[tileKey]["inverse_corner"] = self.tileKey[tileKey]["corner"] # Sets the inverse_corner to the normal corner


    # This loads all of the tile's animations
    def load_tile_anims(self):
        self.tileAnims = {}

        for tile, anims in constants.TILES_WITH_ANIMATIONS.items():
            self.tileAnims[tile] = {}
            
            for animName, data in anims["animations"].items():
                self.tileAnims[tile][animName] = src.animation.Animation(
                    data["delay"],
                    data["path"], 
                    constants.TILE_SIZE[0] 
                )


    def setup_room_tile_anims(self):
        currentRoom = self.levels[self.level][self.room] # For convenience

        self.individualTileAnims = {} # A dictionary of all INDIVIDUAL tile's animation objects

        # Iterating through all of the tiles in the current room
        for y, row in enumerate(currentRoom):
            for x, tile in enumerate(row):

                if tile in constants.TILES_WITH_ANIMATIONS:
                    # If the tile has an animation
                    self.individualTileAnims[(x, y)] = ("default", self.tileAnims[tile]["default"].copy())


    def render_tiles_with_anims(self, window):
        # individualTileAnims is layed out like this:
        #     (x, y): (animName, animationObject)

        for tilePos, anim in self.individualTileAnims.items():
            frame = anim[1].get_frame()
            
            frame = pygame.transform.flip(frame, False, tilePos[1] >= constants.GRAV_BEAM_TILE_Y_POS) # Flipping the frame

            window.blit(frame, (tilePos[0] * constants.TILE_SIZE[0], tilePos[1] * constants.TILE_SIZE[1]))


    # Sets up the player, given a position or using the level to find the starting position
    def setup_player(
        self, 
        playerX = -1, 
        playerY = -1,
        velocity = 0
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

        self.player = src.player.Player(playerStart, velocity) # Creating the player object based on the position found/given


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
        playerState = self.player.update(self.levels[self.level][self.room], inputs) # Updating the player with the inputs

        # If the player moved to the far right of the screen
        if playerState == "right":
            self.room += 1
            
            # If the room number has hit the end of the level
            if self.room >= len(self.levels[self.level]):
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
        
        # If the return result was of a tile
        # Play the "struck" animation for the tile
        elif playerState != "alive":
            self.individualTileAnims[playerState[1]] = ("struck", self.tileAnims[playerState[0]]["struck"].copy())
        
        # Gravity beam animation update
        self.gravityBeam.update()

        # Ellipse update
        self.ellipse.update(self.room, self.level, self.levels[self.level][self.room])

        # Updating all individual tile's animations
        for tilePos, i in self.individualTileAnims.items():
            tileAnimName, tileAnim = i
            
            result = tileAnim.update()
            
            if not result: # If the animation finished playing
                if tileAnimName != "default":
                    self.individualTileAnims[tilePos] = (
                        "default", 
                        self.tileAnims[self.levels[self.level][self.room][tilePos[1]][tilePos[0]]]["default"].copy()
                    )


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


    # This function renders the tiles onto a given surface
    def draw_tiles(self, surface):
        currentRoom = self.levels[self.level][self.room] # For convenience

        """  BEWARE: SPAGHETTI CODE AHEAD  """ # Maybe I should clean this up a bit...
        # Iterating through all of the tiles in the current room
        for y, row in enumerate(currentRoom): 
            for x, tile in enumerate(row):

                if tile in self.tileKey: # If it is a solid block
                    # Drawing the tile at the position
                    surface.blit(
                        self.tileKey[tile]["tile"],
                        (x * constants.TILE_SIZE[0],
                        y * constants.TILE_SIZE[1])
                    )

                    """  RENDERING EDGES  """
                    # Offset is the direction in which the program is checking in relation to the tile being drawn
                    for offset in range(-1, 2):
                        # VERTICAL EDGES
                        if self.check_tile(currentRoom, x + offset, y): # If the tile being checked in relation to the tile being rendered is on the screen and transparent

                            # Creates the image of the edge with a rotation based on which direction the offset is checking. 
                            # These are the vertical edges.
                            image = pygame.transform.rotate(
                                self.tileKey[tile]["edge"], 
                                0 if offset == -1 else 180
                            )

                            surface.blit(
                                image,
                                (x * constants.TILE_SIZE[0] + (0 if offset == -1 else constants.TILE_SIZE[0] - image.get_width()), # Finds the X coordinates of the vertical edge based on the direction being checked
                                y * constants.TILE_SIZE[1])
                            )

                        # HORIZONTAL EDGES
                        if self.check_tile(currentRoom, x, y + offset): # If the tile being checked in relation to the tile being rendered is on the screen and transparent

                            # Creates an image with a rotation based on the direction the program is checking. 
                            # These are the horizontal edges.
                            image = pygame.transform.rotate(
                                self.tileKey[tile]["edge"], 
                                270 if offset == -1 else 90
                            )

                            surface.blit(
                                image,
                                (x * constants.TILE_SIZE[0],
                                y * constants.TILE_SIZE[1] + (0 if offset == -1 else constants.TILE_SIZE[0] - image.get_height())) # Finds the Y position of the horizontal edge
                            )
                    
                    # Corners have to be drawn ontop of the edges

                    """  RENDERING CORNERS  """
                    # This goes through all the tiles surrounding the tile
                    for offset in range(-1, 2):
                        for offset2 in range(-1, 2):

                            if (
                                # If the tile being checked is a corner and not an edge
                                offset != 0 and offset2 != 0 and 
                                # If the tile the corner is facing is on the screen
                                utility.check_between((x + offset2, y + offset), (0, 0), constants.SCREEN_TILE_SIZE)
                                ):
                                    # These are for checks
                                    edgeT1 = currentRoom[y + offset][x] in constants.TRANSPARENT_TILES # If the edge in one direction of the corner is transparent
                                    edgeT2 = currentRoom[y][x + offset2] in constants.TRANSPARENT_TILES # If the edge in the other direction of the corner is transparent
                                    corner = currentRoom[y + offset][x + offset2] in constants.TRANSPARENT_TILES # If the corner is transparent

                                    selectedImage = None

                                    if edgeT1 and edgeT2:  # If both edges are transparent
                                        selectedImage = self.tileKey[tile]["corner"]

                                    elif not edgeT1 and not edgeT2 and corner: # If both edges are not transparent and the corner is
                                        selectedImage = self.tileKey[tile]["inverse_corner"]
                                    
                                    if selectedImage != None:
                                        image = pygame.transform.rotate(
                                            selectedImage, 
                                            -90 if (offset, offset2) == (-1, 1) else (45 * (offset + 1) + 45 * (offset2 + 1)) # Finds the degree of rotation based on the position of the corner
                                        )

                                        surface.blit(
                                            image,
                                            (x * constants.TILE_SIZE[0] + (0 if offset2 == -1 else constants.TILE_SIZE[0] - image.get_width()), # Finds the X position of the corner image
                                            y * constants.TILE_SIZE[1] + (0 if offset == -1 else constants.TILE_SIZE[0] - image.get_height())) # Finds the y position of the corner image
                                        )

                elif tile in constants.TRANSPARENT_TILES: # If the tile is transparent
                    # Transparent tiles also draw the background behind them, and may have special properties.

                    # Drawing the background tile
                    surface.blit(
                        self.background,
                        (x * constants.TILE_SIZE[0],
                        y * constants.TILE_SIZE[1])
                    )

                    # If the tile is a spike
                    if tile in constants.SPIKE_ROTATIONS:
                        # Draw the spike with rotation based on the tile
                        # For example, a tile which is a greater than sign (>) will be a spike rotated to face the right.
                        surface.blit(
                            pygame.transform.rotate(self.spikeTile, constants.SPIKE_ROTATIONS[tile]),
                            (x * constants.TILE_SIZE[0],
                            y * constants.TILE_SIZE[1])
                        )


    # Renders everything to the screen
    def render(self, window):
        super().render()

        if self.tilesChanged: # If the tiles have changed, rerender them
            self.tileSurface.fill((0, 0, 0))
            self.draw_tiles(self.tileSurface)
            
            self.tilesChanged = False

            self.setup_room_tile_anims()
        
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