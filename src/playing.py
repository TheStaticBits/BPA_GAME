from typing import List
import src.scene_base
import src.saving

class Playing(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__()

        self.level = src.saving.get_level()


    def update(self):
        super().update()

    
    def render(self):
        super().render()