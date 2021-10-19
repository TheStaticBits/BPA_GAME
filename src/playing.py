"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import src.scene_base
import src.utility

class Playing(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__()

        self.level = 0
        self.room = 0


    def update(self):
        super().update()

    
    def render(self):
        super().render()