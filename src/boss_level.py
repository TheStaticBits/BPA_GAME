import pygame

import src.base_level
import src.tile_renderer
import src.belloq
import src.big_bite
import src.constants as constants

class BossLevel(src.base_level.BaseLevel):
    def __init__(self, saveData):
        super().__init__(saveData, __name__)

        self.tileRenderers = []

        for x in range(2):
            self.tileRenderers.append(src.tile_renderer.TileRenderer())

        self.tileSurfaces = []

        self.playerRoomIndex = 0 # This is the index in the list of tile surfaces that the player is in

        self.tilesOffset = 0

        # Transparent surface used for entity rendering
        self.empty_surf = pygame.Surface(constants.SCREEN_SIZE, flags = pygame.SRCALPHA)
        
        self.bossName = None


    def setup(self, boss, level, room):
        self.level = level
        self.room = room
        
        self.load_rooms()
        self.start_music()
        self.check_entity_rendering()
        self.reset_all()

        if boss == "Belloq":
            self.boss = src.belloq.Belloq()
            self.bossName = "Belloq"
        
        elif boss == "Big Bite":
            self.boss = src.big_bite.BigBite()
            self.bossName = "Big Bite"

        self.minOffset = -((len(self.levels[self.level]) - 1) * constants.SCREEN_SIZE[0])

    
    def load_rooms(self):
        self.tileSurfaces.clear()

        for count, tr in enumerate(self.tileRenderers):
            # self.room is the room that the player is in
            room = self.room + count - self.playerRoomIndex

            if room > len(self.levels[self.level]) - 1:
                room = len(self.levels[self.level]) - 1

            surf = pygame.Surface(constants.SCREEN_SIZE)

            tr.draw_tiles(
                self.levels[self.level][room], 
                surf, 
                self.levelData[self.level]["background"],
                level = self.levels[self.level],
                roomNumber = room
            )
            self.tileSurfaces.append(surf)
            
            tr.setup_room_tile_anims(self.levels[self.level][room])

    
    def update(self, inputs):
        playerState = super().update(
            inputs, 
            self.tileRenderers[self.playerRoomIndex],
            playerSpawnOffset = 0 # change maybe soon
        )

        if playerState == "right":
            if self.room == 0:
                if self.check_for_boss():
                    self.setup(self.levelData[self.level]["boss"], self.level, 0)
                
                elif cutscene := self.check_for_cutscene():
                    return cutscene
                
                else:
                    return "playing"
            
            else:
                if dir == "right":
                    self.playerRoomIndex = 1
                
        elif playerState == "left":
            self.playerRoomIndex = 0
            self.load_rooms()
        
        elif playerState == "dead":
            self.boss.reset()
            self.playerRoomIndex = 0
            self.room = 0
            self.load_rooms()

        self.tilesOffset = -(self.player.rect.x + (constants.PLAYER_WIDTH // 2) - (constants.SCREEN_SIZE[0] // 2))

        checkTileOffset = self.tilesOffset - (constants.SCREEN_SIZE[0] * self.room)

        if checkTileOffset > 0:
            self.tilesOffset = 0

        elif checkTileOffset < self.minOffset:
            self.tilesOffset = self.minOffset + (constants.SCREEN_SIZE[0] * self.room)
        
        if self.playerRoomIndex == 1:
            if self.tilesOffset <= 0:
                self.playerRoomIndex = 0
                self.load_rooms()
        
        elif self.playerRoomIndex == 0:
            if self.tilesOffset > 0:
                self.playerRoomIndex = 1
                self.load_rooms()
                
        for tr in self.tileRenderers:
            tr.update_tiles_with_anims() # Update any tiles that have animations
        
        if self.bossName == "Belloq":
            dead = self.boss.update(
                self.player, 
                self.room, 
                len(self.levels[self.level]), 
                self.tilesOffset
            )

        elif self.bossName == "Big Bite":
            dead = self.boss.update(
                self.player.get_mask(), 
                self.player.rect.topleft, 
                self.tilesOffset,
                self.room
            )

        if dead:
            self.boss.reset()
            self.playerRoomIndex = 0
            self.room = 0
            self.load_rooms()
            self.reset_all()
    
    
    def render(self, window):
        window.blit(self.tileSurfaces[self.playerRoomIndex], (self.tilesOffset, 0))
        self.tileRenderers[self.playerRoomIndex].render_tiles_with_anims(window, self.gravityDir, offset = self.tilesOffset)

        if self.playerRoomIndex == 0:
            otherRoomIndex = 1
            otherRoomX = self.tilesOffset + constants.SCREEN_SIZE[0]
        else:
            otherRoomIndex = 0
            otherRoomX = self.tilesOffset - constants.SCREEN_SIZE[0]
            
        window.blit(self.tileSurfaces[otherRoomIndex], (otherRoomX, 0))
        self.tileRenderers[otherRoomIndex].render_tiles_with_anims(window, self.gravityDir, offset = otherRoomX)

        entitiesSurf = self.empty_surf.copy()
        super().render(
            entitiesSurf, 
            offset = self.tilesOffset, 
            renderWithCheck = (self.tilesOffset == 0)
        )
        window.blit(entitiesSurf, (0, 0))

        self.boss.render(window, self.tilesOffset, self.room)

        super().render_grav_beam(window)
        super().render_screen_shadow(window)