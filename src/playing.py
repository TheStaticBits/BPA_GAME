"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

RENDERING_METHOD = 0 # 0 for the preset method which involves the spritesheet of all tiles, 1 for the newer method
# This changes how the game renders tiles

import pygame

from math import floor

import src.scene_base
import src.utility
import src.constants

class Playing(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__()

        self.levels = src.utility.load_levels()

        self.level = 0
        self.room = 0

        self.tileset = src.utility.load_spritesheet("res/tileset_test.png", 16)

        self.tile = pygame.image.load("res/other_tile_test/tile.png")
        self.edge = pygame.image.load("res/other_tile_test/edge.png")


    def update(self, mousePos, mousePressed):
        super().update()

        tilePos = (
            floor(mousePos[0] / src.constants.TILE_SIZE[0]),
            floor(mousePos[1] / src.constants.TILE_SIZE[1])
        )

        if mousePressed["left"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = "w"

        if mousePressed["right"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "

    
    def render(self, window):
        super().render()

        currentRoom = self.levels[self.level][self.room]

        """   BEWARE: *SPAGHETTI CODE* AHEAD   """
        for y in range(src.constants.SCREEN_TILE_SIZE[1]):
            for x in range(src.constants.SCREEN_TILE_SIZE[0]):
                tile = currentRoom[y][x]

                if tile == "w":
                    if RENDERING_METHOD == 0:
                        try:
                            tileSurroundings = (
                                (currentRoom[y - 1][x - 1], currentRoom[y - 1][x], currentRoom[y - 1][x + 1]),
                                (currentRoom[y][x - 1], currentRoom[y][x], currentRoom[y][x + 1]),
                                (currentRoom[y + 1][x - 1], currentRoom[y + 1][x], currentRoom[y + 1][x + 1]),
                            )
                        except IndexError:
                            #print(x, y)
                            continue

                        for tileNumber, tileKey in enumerate(src.constants.TILESET_KEY):
                            check = True
                            for i, row in enumerate(tileKey):
                                for l, tileType in enumerate(row):
                                    tileToTest = tileSurroundings[i][l]

                                    if tileType == 1:
                                        if tileToTest != tile:
                                            check = False

                                    elif tileType == 0:
                                        if tileToTest != " ":
                                            check = False
                            
                            if check:
                                tileSelected = tileNumber
                                break
                        
                        try:
                            window.blit(
                                self.tileset[tileSelected], 
                                (x * src.constants.TILE_SIZE[0], 
                                y * src.constants.TILE_SIZE[1])
                            )
                        except UnboundLocalError as error:
                            print("ERROR: Tile type does not exist.")


                    elif RENDERING_METHOD == 1:
                        window.blit(
                            self.tile, 
                            (x * src.constants.TILE_SIZE[0], 
                            y * src.constants.TILE_SIZE[1])
                        )

                        for i in range(-1, 2):
                            for l in range(-1, 2):

                                if currentRoom[y + i][x + l] == " ":
                                    
                                    if i == 0 or l == 0: # If it's an edge
                                        if i == 0: # If it's vertical
                                            for height in range(src.constants.TILE_SIZE[1] // self.edge.get_height()):
                                                window.blit(
                                                    self.edge,
                                                    (x * src.constants.TILE_SIZE[0] + ((l + 1) * ((src.constants.TILE_SIZE[0] - self.edge.get_height()) / 2)),
                                                    y * src.constants.TILE_SIZE[1] + (height * self.edge.get_height()) + ((i) * ((src.constants.TILE_SIZE[1] - self.edge.get_height()) / 2)))
                                                )

                                        else: # If it's horizontal
                                            for width in range(src.constants.TILE_SIZE[0] // self.edge.get_width()):
                                                window.blit(
                                                    self.edge,
                                                    (x * src.constants.TILE_SIZE[0] + (width * self.edge.get_width()) + ((l) * ((src.constants.TILE_SIZE[0] - self.edge.get_width()) / 2)),
                                                    y * src.constants.TILE_SIZE[1] + ((i + 1) * ((src.constants.TILE_SIZE[1] - self.edge.get_height()) / 2)))
                                                )
                                    else: # If it's a corner
                                        window.blit(
                                            self.edge,
                                            (x * src.constants.TILE_SIZE[0] + ((l + 1) * ((src.constants.TILE_SIZE[0] - self.edge.get_width()) / 2)),
                                            y * src.constants.TILE_SIZE[1] + ((i + 1) * ((src.constants.TILE_SIZE[1] - self.edge.get_height()) / 2)))
                                        )