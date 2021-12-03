import pygame

import src.base_level
import src.tile_renderer
import src.belloq

class BossLevel(src.base_level.BaseLevel):
    def __init__(self, saveData):
        super().__init__(saveData, __name__)

        self.tileRenderers = []

        for x in range(2):
            self.tileRenderers.append(src.tile_renderer.TileRenderer)

        self.tileSurfaces = []

        self.tilesOffset = 0


    def switch_boss_and_level(self, boss, level, room):
        self.level = level
        self.room = room

        if boss == "belloq":
            self.boss = src.belloq.Belloq()

    
    def load_rooms(self):
        self.maxOffset = ((len(self.levels) - 1 * constants.SCREEN_WIDTH[0]))
        self.tileSurfaces.clear()

        for count, tr in enumerate(self.tileRenderers):
            # self.room is the room that the player is in            
            room = self.room + count * (
                -(self.tilesOffset < (self.room * constants.SCREEN_SIZE[0])) + (self.tilesOffset > (self.room * constants.SCREEN_SIZE[0])) # Finds the room to be rendered through the count, which starts at zero and can move left/right based on the offset of the tiles
            )

            surf = pygame.Surface(constants.SCREEN_WIDTH)

            tr.draw_tiles(
                self.levels[self.level][room], 
                surf, 
                self.levelData[self.level]["background"]
            )
            self.tileSurfaces.append(surf)
            
            tr.setup_room_tile_anims(self.levels[self.level][room])

    
    def update(self, inputs):
        super().update(
            inputs, 
            self.tileRenderers[0],
            playerSpawnOffset = 0
        )

        self.tilesOffset = self.player.rect.x + (constants.PLAYER_WIDTH // 2) - constants.SCREEN_WIDTH[0]

        if self.tilesOffset < 0:
            self.tilesOffset = 0

        elif self.tilesOffset > self.maxOffset:
            self.tilesOffset = self.maxOffset


        for tr in self.tileRenderers:
            tr.update_tiles_with_anims()
        
        self.boss.update(self.player)
    
    
    def render(self, window):
        super().render()