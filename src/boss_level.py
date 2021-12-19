import pygame

import src.base_level
import src.tile_renderer
import src.belloq
import src.big_bite
import src.red_stare
import src.constants as constants

"""
This class, BossLevel, inherits all of the base level functionality from the BaseLevel class.
It adds onto the BaseLevel class by handling screen scrolling and the boss objects
"""
class BossLevel(src.base_level.BaseLevel):
    def __init__(self):
        # Initializes all class variables

        super().__init__(__name__) # Initializes the entities, player, gravity beam, and more

        self.tileRenderers = []

        # Creates two tile renderers
        for x in range(2):
            self.tileRenderers.append(src.tile_renderer.TileRenderer())
        # The list of tileRenderers is two long because there can only be two rooms on screen at once.

        self.tileSurfaces = [] # Used to store the two Pygame Surface objects which have the rooms on them

        self.playerRoomIndex = 0 # This is the index in the list of tile surfaces that the player is in
        # So the playerRoomIndex is zero when the player is in the room on the left
        # And 1 when the player reaches the next room

        self.tilesOffset = 0

        # Transparent surface used for entity rendering
        self.empty_surf = pygame.Surface(constants.SCREEN_SIZE, flags = pygame.SRCALPHA)
        
        self.bossName = None


    def setup(self, boss, level, crystal):
        # Sets up the boss level with a given boss and level
        # It also starts the music and loads the room images.

        self.level = level

        if crystal: super().remove_crystal(level)
        else: super().reset_crystal(level)
        
        super().reset_all()
        super().check_entity_rendering()
        self.load_rooms()
        super().start_music()

        self.bosses = {}

        if "Belloq" in boss:
            self.bosses["Belloq"] = src.belloq.Belloq()
        
        if "Big Bite" in boss:
            self.bosses["Big Bite"] = src.big_bite.BigBite()
        
        if "Red Stare" in boss:
            self.bosses["Red Stare"] = src.red_stare.RedStare()

        # The minimum tile offset that it can be 
        # so, when the player reaches the end of the level, it can't scroll off the screen
        self.minOffset = -((len(self.levels[self.level]) - 1) * constants.SCREEN_SIZE[0])
        # This is minimum because the tileOffset goes negative, not positive.
    

    def restart_level(self):
        if self.currentCrystal: super().reset_crystal(self.level)

        super().reset_all()
        for boss in self.bosses.values():
            boss.reset()
        self.playerRoomIndex = 0
        self.room = 0
        self.load_rooms()

    
    def load_rooms(self):
        # Renders the rooms to a Pygame Surface and adds that to the tileSurface list

        self.tileSurfaces.clear()

        # iterating through the tileRenderer objects
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
            
            # Sets up all tiles with animations into the tileRenderer object
            tr.setup_room_tile_anims(self.levels[self.level][room])

    
    def update(self, window):
        # Updates everything in the boss level, such as the boss object, the player, and the tile rendering offset

        playerState = super().update(
            window.inputs, 
            self.tileRenderers[self.playerRoomIndex],
            playerSpawnOffset = 0 # change maybe soon
        )

        if playerState == "right": # If the player moved to the next room or level
            # If the room variable was reset (by the BaseLevel class), meaning the player moved to the next level
            if self.room == 0: 
                return self.level
        
        elif playerState == "dead":
            self.restart_level()
        
        elif playerState == "crystal":
            return "crystal"

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
        
        for name, boss in self.bosses.items():
            if name == "Belloq":
                dead = boss.update(
                    self.player, 
                    self.room, 
                    len(self.levels[self.level]), 
                    self.tilesOffset
                )

            elif name == "Big Bite":
                dead = boss.update(
                    self.player.get_mask(), 
                    self.player.rect.topleft, 
                    self.tilesOffset,
                    self.room
                )
            
            elif name == "Red Stare":
                dead = boss.update(
                    self.player,
                    self.room,
                    self.tilesOffset
                )

            if dead: 
                self.restart_level()
                break
    
    
    def render(self, window):
        window.blit(self.tileSurfaces[self.playerRoomIndex], (self.tilesOffset, 0))
        self.tileRenderers[self.playerRoomIndex].render_tiles_with_anims(window, self.gravityDir, self.gravBeamYPos, offset = self.tilesOffset)

        if self.playerRoomIndex == 0:
            otherRoomIndex = 1
            otherRoomX = self.tilesOffset + constants.SCREEN_SIZE[0]
        else:
            otherRoomIndex = 0
            otherRoomX = self.tilesOffset - constants.SCREEN_SIZE[0]
            
        window.blit(self.tileSurfaces[otherRoomIndex], (otherRoomX, 0))
        self.tileRenderers[otherRoomIndex].render_tiles_with_anims(window, self.gravityDir, self.gravBeamYPos, offset = otherRoomX)

        entitiesSurf = self.empty_surf.copy()
        super().render(
            entitiesSurf, 
            offset = self.tilesOffset, 
            renderWithCheck = (self.tilesOffset == 0)
        )
        window.blit(entitiesSurf, (0, 0))

        for boss in self.bosses.values():
            boss.render(window, self.tilesOffset, self.room)

        super().render_grav_beam(window)
        super().render_screen_shadow(window)