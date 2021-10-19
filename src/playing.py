from typing import List
import src.scene_base
import src.utility

class Playing(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__()

        self.level = src.saving.check_level()

    def update(self):
        super().update()
    
    def render(self):
        super().render()