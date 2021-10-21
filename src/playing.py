"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

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


    def update(self):
        super().update()

    
    def render(self, window):
        super().render()

        currentRoom = self.levels[self.level][self.room]
        
        # BEWARE: SPAGHETTI CODE AHEAD
        for y in range(src.constants.SCREEN_TILE_SIZE[1]):
            for x in range(src.constants.SCREEN_TILE_SIZE[0]):
                tile = currentRoom[y][x]

                if tile == "w":
                    tileSurroundings = (
                        (currentRoom[y - 1][x - 1], currentRoom[y - 1][x], currentRoom[y - 1][x + 1]),
                        (currentRoom[y][x - 1], currentRoom[y][x], currentRoom[y][x + 1]),
                        (currentRoom[y + 1][x - 1], currentRoom[y + 1][x], currentRoom[y + 1][x + 1]),
                    )

                    for tileNumber, tileKey in src.constants.TILESET_KEY.items():
                        check = True
                        for y, row in enumerate(tileKey):
                            for x, tileType in enumerate(row):
                                tileToTest = tileSurroundings[y][x]

                                if tileType == 1:
                                    if tileToTest != tile:
                                        check = False

                                elif tileType == 0:
                                    if tileToTest != " ":
                                        check = False
                        
                        if check:
                            tileSelected = tileNumber
                            break
                    
                    window.blit(
                        self.tileset[tileNumber], 
                        (x * src.constants.TILE_SIZE[0], 
                        y * src.constants.TILE_SIZE[1])
                    )