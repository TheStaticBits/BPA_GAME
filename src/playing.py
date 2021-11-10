"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import pygame

from math import floor

import src.scene_base
import src.player
import src.utility as utility
import src.constants as constants

class Playing(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__()

        self.levels = utility.load_levels()

        self.level = 0
        self.room = 1

        self.load_tiles()
        self.setup_player()

        self.background = self.tileKey["w"]["tile"].convert_alpha().copy()
        self.background.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)
    
    
    def load_tiles(self):
        self.tileKey = {}

        for tileKey in constants.TILE_KEYS:
            self.tileKey[tileKey] = {
                "tile": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/tile.png").convert(),
                "corner": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/corner.png").convert(),
                "vertical": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/vertical.png").convert(),
                "horizontal": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/horizontal.png").convert()
            }


    def setup_player(self):
        playerStart = (0, 0)

        for y, row in enumerate(self.levels[self.level][self.room]):
            for x, tile in enumerate(row):
                if tile == "p":
                    playerStart = (
                        x * constants.TILE_SIZE[0],
                        y * constants.TILE_SIZE[1]
                    )
                    self.levels[self.level][self.room][y][x] = " "

        self.player = src.player.Player(playerStart)


    def update(self, inputs, mousePos, mousePressed):
        super().update()

        self.player.update(self.levels[self.level][self.room], inputs)

        tilePos = (
            floor(mousePos[0] / constants.TILE_SIZE[0]),
            floor(mousePos[1] / constants.TILE_SIZE[1])
        )

        if mousePressed["left"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = "c"

        if mousePressed["right"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "

    
    def render(self, window):
        super().render()

        currentRoom = self.levels[self.level][self.room]

        """   BEWARE: *SPAGHETTI CODE* AHEAD   """
        for y in range(constants.SCREEN_TILE_SIZE[1]):
            for x in range(constants.SCREEN_TILE_SIZE[0]):
                tile = currentRoom[y][x]

                if tile in self.tileKey:
                    window.blit(
                        self.tileKey[tile]["tile"], 
                        (x * constants.TILE_SIZE[0], 
                        y * constants.TILE_SIZE[1])
                    )

                    for i in range(-1, 2):
                        for l in range(-1, 2):
                            if utility.check_between((x + l, y + i), (0, 0), constants.SCREEN_TILE_SIZE) and currentRoom[y + i][x + l] == " ":
                                
                                if i == 0 or l == 0: # If it's an edge
                                    if i == 0: # If it's vertical
                                        window.blit(
                                            self.tileKey[tile]["vertical"],
                                            (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - self.tileKey[tile]["vertical"].get_width()),
                                            y * constants.TILE_SIZE[1])
                                        )

                                    else: # If it's horizontal
                                        window.blit(
                                            self.tileKey[tile]["horizontal"],
                                            (x * constants.TILE_SIZE[0],
                                            y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - self.tileKey[tile]["horizontal"].get_height()))
                                        )

                                else: # If it's a corner
                                    window.blit(
                                        self.tileKey[tile]["corner"],
                                        (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - self.tileKey[tile]["corner"].get_width()),
                                        y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - self.tileKey[tile]["corner"].get_height()))
                                    )

                elif tile == " ":
                    window.blit(
                        self.background, 
                        (x * constants.TILE_SIZE[0], 
                        y * constants.TILE_SIZE[1])
                    )
    
        self.player.render(window)