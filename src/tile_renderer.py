"""
This renderer 
"""

import pygame
import os

import src.animation
import src.constants as constants
import src.utility as utility

class TileRenderer:
    def __init__(self):
        self.load_tiles()
        self.load_tile_anims()

        # Loading spike tile
        self.spikeTile = pygame.image.load(constants.SPIKE_PATH).convert_alpha()

        # If the tile being checked is on the screen and transparent, used when drawing edges to the screen
        self.check_tile = lambda room, x, y: utility.check_between((x, y), (0, 0), constants.SCREEN_TILE_SIZE) and room[y][x] in constants.TRANSPARENT_TILES 
        
        # Setting up background tile
        self.background = self.tileKey["w"]["tile"].convert_alpha().copy()
        self.background.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)
    

    def load_tiles(self):
        # Creating a dictionary
        # Keys are the letter used to represent the tile
        self.tileKey = {}

        for tileKey in constants.TILE_KEYS:
            # Setting the key to another dictionary with the individual parts of the tile image
            self.tileKey[tileKey] = {
                "tile": pygame.image.load(f"res/tiles/solid/{constants.TILE_KEYS[tileKey]}/tile.png").convert_alpha(),
                "corner": pygame.image.load(f"res/tiles/solid/{constants.TILE_KEYS[tileKey]}/corner.png").convert_alpha(),
                "edge": pygame.image.load(f"res/tiles/solid/{constants.TILE_KEYS[tileKey]}/edge.png").convert_alpha(),
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


    def setup_room_tile_anims(self, levels, levelNum, roomNum):
        currentRoom = levels[levelNum][roomNum] # For convenience

        self.individualTileAnims = {} # A dictionary of all INDIVIDUAL tile's animation objects

        # Iterating through all of the tiles in the current room
        for y, row in enumerate(currentRoom):
            for x, tile in enumerate(row):

                if tile in constants.TILES_WITH_ANIMATIONS:
                    # If the tile has an animation
                    self.individualTileAnims[(x, y)] = {
                        "tile": tile, 
                        "animationName": "default", 
                        "animationObject": self.tileAnims[tile]["default"].copy()
                    }


    def render_tiles_with_anims(self, window, gravityDir):
        for tilePos, anim in self.individualTileAnims.items():
            frame = anim["animationObject"].get_frame()

            flip = tilePos[1] >= constants.GRAV_BEAM_TILE_Y_POS

            if gravityDir == -1:
                flip = not flip
            
            frame = pygame.transform.flip(frame, False, flip) # Flipping the frame

            window.blit(frame, (tilePos[0] * constants.TILE_SIZE[0], tilePos[1] * constants.TILE_SIZE[1]))


    def update_tiles_with_anims(self):
        # Updating all individual tile's animations
        # Removes all crystals after they're done playing the "struck" animation
        removeTiles = [] # List of tiles to remove from the individualTileAnims dictionary
        for tilePos, anim in self.individualTileAnims.items():
            result = anim["animationObject"].update()
            
            if not result: # If the animation finished playing
                if anim["animationName"] != "default":
                    if anim["tile"] != "c":
                        self.individualTileAnims[tilePos]["animationObject"] = self.tileAnims[anim["tile"]]["default"].copy()
                        self.individualTileAnims[tilePos]["animationName"] = "default"
                    
                    else:
                        removeTiles.append(tilePos)
        
        for tilePos in removeTiles:
            del self.individualTileAnims[tilePos]


    def change_tile_anim(self, tile, pos, animationName) -> bool:
        if self.individualTileAnims[pos]["animationName"] != animationName:
            self.individualTileAnims[pos]["animationName"] = "struck"
            self.individualTileAnims[pos]["animationObject"] = self.tileAnims[tile]["struck"].copy()

            return True

        else:
            return False


    # This function renders the SOLID tiles onto a given surface
    def draw_tiles(self, levels, levelNum, roomNum, surface) -> "pygame.Surface":
        currentRoom = levels[levelNum][roomNum] # For convenience

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