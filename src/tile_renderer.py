import pygame
import os

import src.animation
import src.constants as constants
import src.utility as utility

"""
This class handles all of the rendering of tiles, whether they have animations
or not. It loads all tile images and animations as well.
Render tiles without animations through draw_tiles()
and render tiles with animations through render_tiles_with_anims()
after you've initialized the tiles through setup_room_tile_anims()
"""
class TileRenderer:
    def __init__(self):
        self.load_tiles()
        self.load_tile_anims()

        # Loading spike tile
        self.spikeTile = pygame.image.load(constants.SPIKE_PATH).convert_alpha()

        # If the tile being checked is on the screen and transparent, used when drawing edges to the screen
        self.check_tile = lambda room, x, y: utility.check_between((x, y), (0, 0), constants.SCREEN_TILE_SIZE) and room[y][x] in constants.TRANSPARENT_TILES
    

    def check_tile_across_rooms(self, roomNumber, level, x, y):
        # Finds the x position of the tile on the screen next to the one being checked, flipping it over to the other side of the screen
        if x >= constants.SCREEN_TILE_SIZE[0]:
            checkRoomX = 0
            checkRoomNum = roomNumber + 1

        elif x < 0:
            checkRoomX = constants.SCREEN_TILE_SIZE[0] - 1
            checkRoomNum = roomNumber - 1
        
        else:
            return False

        
        if 0 <= checkRoomNum < len(level): # If the room being checked is not the first or last room in the level
            # Checks if the tile is transparent and returns that
            return level[checkRoomNum][y][checkRoomX] in constants.TRANSPARENT_TILES
        
        return False

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
    

    def load_tile_anims(self):
        # Loads all the animations that tiles could have
        # creates a dictionary, tileAnim, that can be accessed through:
        # self.tileAnims[tileLetter][animationName]
        # Where tileLetter is the letter that represents the tile, such as "j" for jump orbs

        self.tileAnims = {}

        for tile, anims in constants.TILES_WITH_ANIMATIONS.items():
            self.tileAnims[tile] = {}
            
            for animName, data in anims.items():
                self.tileAnims[tile][animName] = src.animation.Animation(
                    data["delay"],
                    path = data["path"], 
                    width = constants.TILE_SIZE[0] 
                )


    def setup_room_tile_anims(self, room):
        # Sets up the animation objects for the given room's data

        self.individualTileAnims = {} # A dictionary of all INDIVIDUAL tile's animation objects

        # Iterating through all of the tiles in the current room
        for y, row in enumerate(room):
            for x, tile in enumerate(row):

                if tile in constants.TILES_WITH_ANIMATIONS:
                    # If the tile has an animation
                    self.individualTileAnims[(x, y)] = {
                        "tile": tile, 
                        "animationName": "default", 
                        "animationObject": self.tileAnims[tile]["default"].copy()
                    }


    def get_tile_anim_frame(self, position, globalGravity, gravBeamYPos) -> "pygame.Surface":
        # Gets the frame that the tile is currently in
        
        image = self.individualTileAnims[position]["animationObject"].get_frame()

        flip = position[1] >= gravBeamYPos

        # If the global gravity is reversed, also reverse the tile's image
        if globalGravity == -1: flip = not flip

        return pygame.transform.flip(image, False, flip)


    def render_tiles_with_anims(self, window, globalGravity, gravBeamYPos, offset = 0):
        # Renders all tiles with animations
        # Renders the tiles flipped if they're bellow the gravity line

        for tilePos in self.individualTileAnims:
            frame = self.get_tile_anim_frame(tilePos, globalGravity, gravBeamYPos)

            # Rendering it on the screen
            window.blit(frame, (
                tilePos[0] * constants.TILE_SIZE[0] + offset, 
                tilePos[1] * constants.TILE_SIZE[1]
            ))


    def update_tiles_with_anims(self):
        # Updating all individual tile's animations
        # Removes all crystals after they're done playing the "struck" animation
        removeTiles = [] # List of tiles to remove from the individualTileAnims dictionary
        for tilePos, anim in self.individualTileAnims.items():
            result = anim["animationObject"].update()
            
            if not result: # If the animation finished playing
                if anim["animationName"] != "default":
                    if anim["tile"] != "c":
                        # If the tile's animation is not the default and it's not a crystal, reset it
                        self.individualTileAnims[tilePos]["animationObject"] = self.tileAnims[anim["tile"]]["default"].copy()
                        self.individualTileAnims[tilePos]["animationName"] = "default"
                    
                    else:
                        removeTiles.append(tilePos) # Removing crystals after they're collected
         
        for tilePos in removeTiles:
            del self.individualTileAnims[tilePos]


    def change_tile_anim(self, tile, pos, animationName) -> bool:
        # Changes the tile's animation at a given position
        # Returns True if it wasn't already the animation it was changing it to
        # Or the tile was a holdable tile

        ifNewAnim = self.individualTileAnims[pos]["animationName"] != animationName
        ifHoldable = self.individualTileAnims[pos]["tile"] in constants.HOLDABLE_TILES

        if ifNewAnim or ifHoldable:
            self.individualTileAnims[pos]["animationName"] = "struck"
            self.individualTileAnims[pos]["animationObject"] = self.tileAnims[tile]["struck"].copy()

            if ifNewAnim:
                return True

        return False


    # This function renders the SOLID tiles onto a given surface
    def draw_tiles(
        self, 
        room, 
        surface, 
        backgroundTile,
        level = None, # If it needs to be drawn over multiple levels, with the edges and corners being accurate with the other rooms in the level
        roomNumber = None
        ):
        # Setting up background tile
        backgroundTile = self.tileKey[backgroundTile]["tile"].copy()
        backgroundTile.set_alpha(150)

        # Iterating through all of the tiles in the current room
        for y, row in enumerate(room): 
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
                        check = self.check_tile(room, x + offset, y) # If the tile being checked in relation to the tile being rendered is on the screen and transparent

                        if not check and level is not None:
                            check = self.check_tile_across_rooms(roomNumber, level, x + offset, y)
                        
                        if check:
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
                        if self.check_tile(room, x, y + offset): # If the tile being checked in relation to the tile being rendered is on the screen and transparent

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
                                    edgeTile1 = room[y + offset][x] in constants.TRANSPARENT_TILES # If the edge tile in one direction of the corner is transparent
                                    edgeTile2 = room[y][x + offset2] in constants.TRANSPARENT_TILES # If the edge tile in the other direction of the corner is transparent
                                    if not edgeTile2 and level is not None:
                                        edgeTile2 = self.check_tile_across_rooms(roomNumber, level, x + offset2, y)

                                    corner = room[y + offset][x + offset2] in constants.TRANSPARENT_TILES # If the corner tile is transparent
                                    if not corner and level is not None:
                                        corner = self.check_tile_across_rooms(roomNumber, level, x + offset2, y + offset)

                                    selectedImage = None

                                    if edgeTile1 and edgeTile2:  # If both edges of the corner are transparent
                                        selectedImage = self.tileKey[tile]["corner"]

                                    elif not edgeTile1 and not edgeTile2 and corner: # If both edges are not transparent and the corner is
                                        selectedImage = self.tileKey[tile]["inverse_corner"]
                                    
                                    if selectedImage is not None:
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
                        backgroundTile,
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