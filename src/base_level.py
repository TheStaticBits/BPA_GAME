import pygame

import src.scene_base
import src.constants as constants
import src.utility as utility
import src.ellipse_and_corlen as eac

class BaseLevel(src.scene_base.SceneBase):
    def __init__(self, name):
        super().__init__(name)

        self.cutsceneData = utility.load_json(constants.CUTSCENE_DATA_PATH)

        self.level = 0
        self.room = 0

        # Loading levels from levels.txt
        self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)
        
        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()

        # Gravity line pull direction
        # Each entity still has its own pull direction for if it's below or above the line.
        # 1 is normal gravity (pull towards the line)
        # -1 is reverse gravity (pull away from the line)
        self.gravityDir = 1

        self.currentCrystal = False # If the crystal in the current level has been collected

        # Setting up the player
        self.setup_player(new = True)

        self.setup_entities(self.player.rect.topleft)

        self.playerPositions = [] # List of player positions for Corlen and Ellipse to follow
        self.playerLevelAndRoom = [] # List of the level and room the player is in at what frame
        self.playerFacing = [] # List of what direction the player is facing at what frame

        self.showEntities = True
        self.check_entity_rendering()
        
        self.playingSong = None

        # Setting up gravity beam animation
        self.gravityBeam = src.animation.Animation(
            constants.GRAV_BEAM_DELAY,
            path = constants.GRAV_BEAM_PATH, 
            width = constants.GRAV_BEAM_WIDTH
        )
        self.gravityBeam.set_alpha(150) # Makes gravity beam transparent

        self.gravBeamYPos = constants.GRAV_BEAM_TILE_Y_POS

        # For managing one time presses
        self.pressedButton = None

        self.popupFont = pygame.font.Font(constants.FONT_PATH, 40)

        self.popupText = None
        self.popupRendered = None
        self.popupTextTimer = constants.POPUP_TEXT_DURATION
        self.popupTextAlpha = 255


    def start_music(self):
        if self.playingSong != self.levelData[self.level]["music"]:
            utility.play_music(self.levelData[self.level]["music"])
            self.playingSong = self.levelData[self.level]["music"]
    

    def music_stopped(self):
        self.playingSong = None


    def remove_crystal(self, level):
        # Goes through and removes crystals in the level
        for roomNum, room in enumerate(self.levels[level]):
            for y, row in enumerate(room):
                for x, tile in enumerate(row):
                    if tile == "c":
                        self.levels[level][roomNum][y][x] = " "


    def reset_crystal(self, level):
        levels = utility.load_levels(constants.LEVELS_PATH)[0]

        self.levels[level] = levels[level]


    # Sets up the player, given a position or using the level to find the starting position
    def setup_player(
        self, 
        playerX = -1, 
        playerY = -1,
        yVelocity = 0,
        xVelocity = 0,
        new = False
        ):

        # If there was no data passed in, set the position to the tile "p" in the level
        if playerX == -1 and playerY == -1:
            playerStart = (0, 0)

            # Iterating through the rows in the room
            for y, row in enumerate(self.levels[self.level][self.room]):
                # Iterating through the individual letters in the row
                for x, tile in enumerate(row):
                    if tile == "p":
                        # Setting the player's starting based on the position of the "p" tile
                        playerStart = (
                            x * constants.TILE_SIZE[0],
                            y * constants.TILE_SIZE[1]
                        )

        else: # If there was a position supplied
            playerStart = (playerX, playerY) # Setting the player's start to the given position

        if new:
            self.player = src.player.Player(playerStart, yVelocity, xVelocity) # Creating the player object based on the position found/given
        
        else:
            self.player.reset(playerStart, yVelocity, xVelocity) # Resetting the player's position and velocity


    def setup_entities(self, position):
        self.entities = []

        self.entities.append(eac.create_entity("ellipse", position, self.room, self.level))
        self.entities.append(eac.create_entity("corlen", position, self.room, self.level))

        for ent in self.entities:
            ent.facing = self.player.facing
            ent.gravityDir = self.player.gravityDir


    def reset_all(self):
        self.room = 0 # Resetting the room number
        
        self.setup_player()
        self.setup_entities(self.player.rect.topleft)
        
        self.gravityDir = 1 # Resetting gravity pull
        self.gravBeamYPos = constants.GRAV_BEAM_TILE_Y_POS
        self.pressedButton = None

        self.popupText = None
        
        self.currentCrystal = False

        self.playerPositions.clear()
        self.playerLevelAndRoom.clear()
        self.playerFacing.clear()
    

    def popup(self, text):
        self.popupText = text
        self.popupRendered = self.popupFont.render(text, False, constants.WHITE)
        self.popupTextTimer = constants.POPUP_TEXT_DURATION
        self.popupTextAlpha = 255


    def check_entity_rendering(self):
        if "entities" in self.levelData[self.level]:
            self.showEntities = self.levelData[self.level]["entities"] != "none"
        else:
            self.showEntities = True


    def update(
        self, 
        inputs, # Dictionary of keys pressed
        tileRenderer,
        playerSpawnOffset = 0, # Offset for when the player switches levels/rooms
        ):
        super().update()

        # Updating the popup text if there is any
        if self.popupText is not None:
            if self.popupTextTimer > 0:
                self.popupTextTimer -= 1
            
            else:
                self.popupTextAlpha -= constants.POPUP_TEXT_FADE_SPEED

                if self.popupTextAlpha <= 0:
                    self.popupText = None

        """
        Updating Player
        """
        playerState = self.player.update(
            self.levels[self.level][self.room],
            self.room,
            self.levels[self.level],
            inputs, 
            self.gravBeamYPos,
            globalGravity = self.gravityDir,
            tileRenderer = tileRenderer
        ) # Updating the player with the inputs

        # If the player moved to the far right of the screen
        if playerState == "right":
            self.room += 1
            
            # If the room number has hit the end of the level
            if self.room >= len(self.levels[self.level]):                
                # Resetting the room number and incrementing the level number
                self.room = 0
                self.level += 1
                
                self.start_music()
                self.setup_player()
                self.setup_entities(self.player.rect.topleft)
                self.check_entity_rendering()

                if self.currentCrystal:
                    self.currentCrystal = False
                    return "crystal"

            else:
                self.player.rect.x = -constants.PLAYER_WIDTH - playerSpawnOffset # Moving the player to the complete other side of the room

        # If the player moved to the far left of the screen
        elif playerState == "left":
            if self.room > 0: # If it isn't the start of a level
                self.room -= 1

                self.player.rect.x += constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0]) + playerSpawnOffset # Moving the player to the opposite side of the screen
        
        # If the return result was of a tile
        # Play the "struck" animation for the tile
        elif isinstance(playerState, tuple):
            if tileRenderer.change_tile_anim(playerState[0], playerState[1], "struck"):
                if playerState[0] == "g": # Gravity orb
                    self.gravityDir *= -1 # Changing the gravity direction
                
                elif playerState[0] == "c": # Crystal
                    self.levels[self.level][self.room][playerState[1][1]][playerState[1][0]] = " " # Removing the tile

                    self.currentCrystal = True

                    if "crystal moves on" in self.levelData[self.level]:
                        return "crystal mid-level"
                
                elif playerState[0] == "m": # Gravity Line Button
                    # Changes the gravity beam position by a specified
                    # amount in the level data, in levels.txt
                    # Which is specified as:
                    # button room, buttonX, buttonY = yPosMoved
                    # where those are all integers besides "button"
                    
                    key = f"button {self.room}, {playerState[1][0]}, {playerState[1][1]}"

                    if self.pressedButton != playerState[1]:
                        self.gravBeamYPos += int(self.levelData[self.level][key])
                        self.pressedButton = playerState[1]
                    
                    else:
                        self.gravBeamYPos -= int(self.levelData[self.level][key])
                        self.pressedButton = None

            
        if self.showEntities:
            if self.playerPositions == [] or self.playerPositions[0] != self.player.rect.topleft: # If the player moved
                playerMoved = True

                self.playerPositions.insert(0, self.player.rect.topleft) # inserts at the front of the list
                self.playerLevelAndRoom.insert(0, (self.level, self.room))
                self.playerFacing.insert(0, self.player.facing)
                
                if len(self.playerPositions) > constants.MAX_FOLLOW_DISTANCE + 1:
                    self.playerPositions.pop(-1)
                    self.playerLevelAndRoom.pop(-1)
                    self.playerFacing.pop(-1)
            
            else:
                playerMoved = False

            # Updating Ellipse and Corlen
            for ent in self.entities:
                ent.update(
                    self.levels, 
                    self.playerPositions,
                    self.playerLevelAndRoom,
                    self.playerFacing,
                    playerMoved,
                    self.gravBeamYPos,
                    self.gravityDir
                )
        
        self.gravityBeam.update()

        return playerState
    
    
    def render(self, surface, offset = 0, renderWithCheck = True):
        super().render() # For logging

        if self.showEntities:
            # Drawing Ellipse and Corlen
            for ent in self.entities:
                if renderWithCheck:
                    ent.render_with_check(self.room, self.level, surface, offset = offset)
                
                else:
                    ent.render_move_over(surface, self.room, offset = offset)
        
        # Rendering the player
        self.player.render(surface, offset = offset)
    

    def render_grav_beam(self, surface):
        # Drawing gravity beam
        for x in range(constants.SCREEN_SIZE[0] // constants.GRAV_BEAM_WIDTH): # Goes through the center of the screen
            # Draws the gravity beam
            self.gravityBeam.render(
                surface, 
                (x * constants.GRAV_BEAM_WIDTH, 
                (self.gravBeamYPos * constants.TILE_SIZE[1]) - (self.gravityBeam.images[0].get_height() / 2)) # Centers the beam
            )
    

    def render_popup(self, surface):
        if self.popupText is not None:
            utility.draw_text_with_border(
                surface,
                (constants.SCREEN_SIZE[0] / 2 - self.popupRendered.get_width() / 2, 
                 constants.SCREEN_SIZE[1] / 4 - self.popupRendered.get_height() / 2),
                self.popupText,
                self.popupFont,
                constants.WHITE,
                borderWidth = 2,
                alpha = self.popupTextAlpha
            )
    
    
    def render_screen_shadow(self, surface):
        surface.blit(self.screenShadow, (0, 0))