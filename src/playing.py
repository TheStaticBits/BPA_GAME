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

        self.tile = pygame.image.load("res/other_tile_test/tile.png").convert()
        self.corner = pygame.image.load("res/other_tile_test/corner.png").convert()
        self.edgeUp = pygame.image.load("res/other_tile_test/edge_up.png").convert()
        self.edgeDown = pygame.image.load("res/other_tile_test/edge_down.png").convert()

        self.find_player()


    def find_player(self):
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
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = "w"

        if mousePressed["right"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "

    
    def render(self, window):
        super().render()

        self.player.render(window)

        currentRoom = self.levels[self.level][self.room]

        """   BEWARE: *SPAGHETTI CODE* AHEAD   """
        for y in range(constants.SCREEN_TILE_SIZE[1]):
            for x in range(constants.SCREEN_TILE_SIZE[0]):
                tile = currentRoom[y][x]

                if tile == "w":
                    window.blit(
                        self.tile, 
                        (x * constants.TILE_SIZE[0], 
                        y * constants.TILE_SIZE[1])
                    )

                    for i in range(-1, 2):
                        for l in range(-1, 2):
                            if utility.check_between((x + l, y + i), (0, 0), constants.SCREEN_TILE_SIZE) and currentRoom[y + i][x + l] == " ":
                                
                                if i == 0 or l == 0: # If it's an edge
                                    if i == 0: # If it's vertical
                                        window.blit(
                                            self.edgeUp,
                                            (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - self.edgeUp.get_width()),
                                            y * constants.TILE_SIZE[1])
                                        )

                                    else: # If it's horizontal
                                        window.blit(
                                            self.edgeDown,
                                            (x * constants.TILE_SIZE[0],
                                            y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - self.edgeDown.get_height()))
                                        )
                                else: # If it's a corner
                                    window.blit(
                                        self.corner,
                                        (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - self.corner.get_width()),
                                        y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - self.corner.get_height()))
                                    )