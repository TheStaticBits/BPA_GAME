"""
This file includes the class which manages the playing scene, which includes tiles and collisions and generally everything you will interact with while playing the actual game.
"""

import pygame

from math import floor

import src.scene_base
import src.player
import src.utility as utility
import src.constants as constants
import src.animation

class Playing(src.scene_base.SceneBase):
    def __init__(self, saveData):
        super().__init__()

        self.levels = utility.load_levels()

        self.level = int(saveData["level"])
        self.room = int(saveData["room"])

        self.load_tiles()
        self.setup_player(
            saveData["playerX"], 
            saveData["playerY"],
            saveData["playerVelocity"]
        )

        # Setting up background tile
        self.background = self.tileKey["w"]["tile"].convert_alpha().copy()
        self.background.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)

        # Loading spike tile
        self.spikeTile = pygame.image.load("res/misc/spike.png").convert_alpha()

        # Setup tile drawing surface
        self.tileSurface = pygame.Surface((
            constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0],
            constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]
        ))
        self.draw_tiles(self.tileSurface)
        self.tilesChanged = False

        # Setting up gravity beam animation
        self.gravityBeam = src.animation.Animation(
            constants.GRAV_BEAM_PATH, 
            constants.GRAV_BEAM_WIDTH, 
            constants.GRAV_BEAM_DELAY
        )

        # EDITOR CONTROLS:
        self.placeTile = "c"


    def load_tiles(self):
        self.tileKey = {}

        for tileKey in constants.TILE_KEYS:
            self.tileKey[tileKey] = {
                "tile": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/tile.png").convert_alpha(),
                "corner": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/corner.png").convert_alpha(),
                "edge": pygame.image.load(f"res/tiles/{constants.TILE_KEYS[tileKey]}/edge.png").convert_alpha(),
            }


    def setup_player(
        self, 
        playerX = -1, 
        playerY = -1,
        velocity = 0
        ):

        if playerX == -1 and playerY == -1:
            playerStart = (0, 0)

            for y, row in enumerate(utility.load_levels()[self.level][self.room]):
                for x, tile in enumerate(row):
                    if tile == "p":
                        playerStart = (
                            x * constants.TILE_SIZE[0],
                            y * constants.TILE_SIZE[1]
                        )
        else:
            playerStart = (playerX, playerY)

        self.player = src.player.Player(playerStart, velocity)


    def update(
        self, 
        inputs, 
        mousePos, 
        mousePressed
        ):
        super().update()

        """
        Updating Player
        """
        playerState = self.player.update(self.levels[self.level][self.room], inputs)

        # If the player moved to the far right of the screen
        if playerState == "right":
            self.room += 1
            
            if self.room >= len(self.levels[self.level]):
                self.room = 0
                self.level += 1
                self.setup_player()
            
            else:
                self.player.rect.x -= constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0] - 1)

            self.tilesChanged = True

        # If the player moved to the far left of the screen
        elif playerState == "left":
            if self.room > 0:
                self.room -= 1

                self.player.rect.x += constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0] - 1)

                self.tilesChanged = True

        # If the player died
        elif playerState == "dead":
            self.room = 0
            self.setup_player()
            self.tilesChanged = True

        
        # Gravity beam update
        self.gravityBeam.update()


        """
        Mouse Inputs for Editor
        """
        tilePos = (
            floor(mousePos[0] / constants.TILE_SIZE[0]),
            floor(mousePos[1] / constants.TILE_SIZE[1])
        )

        if mousePressed["left"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = self.placeTile
            self.tilesChanged = True
        
        if mousePressed["center"]:
            self.placeTile = self.levels[self.level][self.room][tilePos[1]][tilePos[0]]

        if mousePressed["right"]:
            self.levels[self.level][self.room][tilePos[1]][tilePos[0]] = " "
            self.tilesChanged = True
        
        # Other editor inputs
        if inputs["space"]:
            utility.save_room(self.level, self.room, self.levels[self.level][self.room])


    def draw_tiles(self, surface):
        currentRoom = self.levels[self.level][self.room]

        """
        BEWARE: *SPAGHETTI CODE* AHEAD
        """
        for y in range(constants.SCREEN_TILE_SIZE[1]):
            for x in range(constants.SCREEN_TILE_SIZE[0]):
                tile = currentRoom[y][x]

                if tile in self.tileKey:
                    surface.blit(
                        self.tileKey[tile]["tile"],
                        (x * constants.TILE_SIZE[0],
                        y * constants.TILE_SIZE[1])
                    )

                    for i in range(-1, 2):
                        for l in range(-1, 2):
                            if utility.check_between((x + l, y + i), (0, 0), constants.SCREEN_TILE_SIZE) and currentRoom[y + i][x + l] in constants.TRANSPARENT_TILES: # If the tile being checked in relation to the tile being rendered is on the screen and transparent

                                if i == 0 and l != 0: # If it's vertical
                                    image = pygame.transform.rotate(
                                        self.tileKey[tile]["edge"], 
                                        0 if l == -1 else 180
                                    )

                                    surface.blit(
                                        image,
                                        (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - image.get_width()),
                                        y * constants.TILE_SIZE[1])
                                    )

                                elif l == 0 and i != 0: # If it's horizontal
                                    image = pygame.transform.rotate(
                                        self.tileKey[tile]["edge"], 
                                        270 if i == -1 else 90
                                    )

                                    surface.blit(
                                        image,
                                        (x * constants.TILE_SIZE[0],
                                        y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - image.get_height()))
                                    )

                                else: # If it's a corner
                                    image = pygame.transform.rotate(
                                        self.tileKey[tile]["corner"], 
                                        -90 if (i, l) == (-1, 1) else (45 * (i + 1) + 45 * (l + 1)) # Finds the degree of rotation based on the position of the corner
                                    )

                                    surface.blit(
                                        image,
                                        (x * constants.TILE_SIZE[0] + (0 if l == -1 else constants.TILE_SIZE[0] - image.get_width()),
                                        y * constants.TILE_SIZE[1] + (0 if i == -1 else constants.TILE_SIZE[0] - image.get_height()))
                                    )

                elif tile in constants.TRANSPARENT_TILES:
                    surface.blit(
                        self.background,
                        (x * constants.TILE_SIZE[0],
                        y * constants.TILE_SIZE[1])
                    )

                    if tile in constants.SPIKE_ROTATIONS:
                        surface.blit(
                            pygame.transform.rotate(self.spikeTile, constants.SPIKE_ROTATIONS[tile]),
                            (x * constants.TILE_SIZE[0],
                            y * constants.TILE_SIZE[1])
                        )


    def render(self, window):
        super().render()

        # Drawing tiles
        if self.tilesChanged:
            self.tileSurface.fill((0, 0, 0))
            self.draw_tiles(self.tileSurface)
            self.tilesChanged = False
        window.blit(self.tileSurface, (0, 0))

        # Drawing gravity beam
        for x in range(
            (constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0]) 
            // constants.GRAV_BEAM_WIDTH
            ):
            self.gravityBeam.render(
                window, 
                (
                    x * constants.GRAV_BEAM_WIDTH, 
                    (constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1] / 2) - (self.gravityBeam.images[0].get_height() / 2) # Centers the beam
                )
            )

        # Drawing player
        self.player.render(window)