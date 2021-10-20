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


    def update(self):
        super().update()

    
    def render(self, window):
        super().render()

        for y in range(src.constants.SCREEN_TILE_SIZE[1]):
            for x in range(src.constants.SCREEN_TILE_SIZE[0]):
                tile = self.levels[self.level][self.room][y][x]
                
                # Interpreting and rendering occurs here.