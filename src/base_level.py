import pygame

import src.scene_base
import src.constants as constants
import src.utility as utility

class BaseLevel(src.scene_base.SceneBase):
    def __init__(self, saveData):
        super().__init__(__name__)

        # Setting data based off of save data from save.db
        self.level = int(saveData["level"])
        self.room = int(saveData["room"])

        # Loading levels from levels.txt
        self.levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)

        # Gravity line pull direction
        # Each entity still has its own pull direction for if it's below or above the line.
        # 1 is normal gravity (pull towards the line)
        # -1 is reverse gravity (pull away from the line)
        self.gravityDir = int(saveData["globalGravity"])

        self.crystals = [int(x) for x in list(saveData["crystals"])] # Converting the saved string to a list of ints
        self.currentCrystal = False # If the crystal in the current level has been collected

        self.remove_collected_crystals() # Removing crystals that are already collected from the levels

        # Setting up the player based on the save data
        self.setup_player(
            float(saveData["playerX"]), 
            float(saveData["playerY"]),
            float(saveData["playerYVelocity"]),
            float(saveData["playerXVelocity"]),
            new = True
        )

        self.setup_entities((self.player.rect.x, self.player.rect.y))

        self.playerPositions = [] # List of player positions for Corlen and Ellipse to follow
        self.playerLevelAndRoom = [] # List of the level and room the player is in at what frame
        self.playerFacing = [] # List of what direction the player is facing at what frame
        
        self.playingSong = ""

        self.tilesChanged = False

        # Setting up gravity beam animation
        self.gravityBeam = src.animation.Animation(
            constants.GRAV_BEAM_DELAY,
            path = constants.GRAV_BEAM_PATH, 
            width = constants.GRAV_BEAM_WIDTH
        )


    def start_music(self):
        utility.play_music(self.levelData[self.level]["music"])
        self.playingSong = self.levelData[self.level]["music"]


    def remove_collected_crystals(self):
        # This is just an amazing tower of for and if statements.
        # It basically goes through and removes all crystals that have already been collected.
        for levelNum, collected in enumerate(self.crystals):
            if collected:
                done = False
                for roomNum, room in enumerate(self.levels[levelNum]):
                    for y, row in enumerate(room):
                        for x, tile in enumerate(row):
                            if tile == "c":
                                self.levels[levelNum][roomNum][y][x] = " "
                                done = True
                                break
                        if done: break
                    if done: break


    def reset_crystal_in_level(self):
        levels = utility.load_levels(constants.LEVELS_PATH)[0]

        self.levels[self.level] = levels[self.level]


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


    def setup_entities(self, position, facing = 1):
        self.entities = []

        self.entities.append(src.ellipse.Ellipse(position, self.room, self.level))
        self.entities.append(src.corlen.Corlen(position, self.room, self.level))

        for ent in self.entities:
            ent.facing = facing
            print(facing)


    def check_for_cutscene(self):
        for name, data in self.cutsceneData.items():
            if self.level == data["beforeLevel"]:
                return name


    def update(
        self, 
        inputs, # Dictionary of keys pressed
        tileRenderer,
        playerSpawnOffset = 0, # Offset for when the player switches levels/rooms
        ):
        super().update()

        """
        Updating Player
        """
        playerState = self.player.update(self.levels[self.level][self.room], inputs, self.gravityDir) # Updating the player with the inputs

        # If the player moved to the far right of the screen
        if playerState == "right":
            self.room += 1
            
            # If the room number has hit the end of the level
            if self.room >= len(self.levels[self.level]):
                if self.currentCrystal:
                    self.crystals[self.level] = 1
                    self.currentCrystal = False
                
                # Resetting the room number and incrementing the level number
                self.room = 0
                self.level += 1
                
                if self.levelData[self.level]["music"] != self.playingSong:
                    utility.play_music(self.levelData[self.level]["music"])
                    self.playingSong = self.levelData[self.level]["music"]
                
                # Resetting the player
                self.setup_player()
                self.player.facing = 1

                self.setup_entities((self.player.rect.x, self.player.rect.y), facing=1)

                check = self.check_for_cutscene()
                if check != None:
                    return check # Switches to the cutscene
            
            else:
                self.player.rect.x = -playerSpawnOffset # Moving the player to the complete other side of the room

            self.tilesChanged = True # This will make the renderer rerender the tiles in the render function

        # If the player moved to the far left of the screen
        elif playerState == "left":
            if self.room > 0: # If it isn't the start of a level
                self.room -= 1

                self.player.rect.x += constants.SCREEN_TILE_SIZE[0] * (constants.TILE_SIZE[0]) - constants.PLAYER_WIDTH + playerSpawnOffset # Moving the player to the opposite side of the screen

                self.tilesChanged = True # Rerendering the tiles

        # If the player died
        elif playerState == "dead":
            self.room = 0 # Resetting the room number
            self.setup_player() # Resetting the player
            self.tilesChanged = True # Rerenders
            self.gravityDir = 1 # Resetting gravity

            # Resetting crystal
            if self.currentCrystal:
                self.reset_crystal_in_level()
                self.currentCrystal = False
        
        # If the return result was of a tile
        # Play the "struck" animation for the tile
        elif playerState != "alive":
            if tileRenderer.change_tile_anim(playerState[0], playerState[1], "struck"):
                if playerState[0] == "g": # Gravity orb
                    self.gravityDir *= -1 # Changing the gravity direction
                
                elif playerState[0] == "c":
                    self.levels[self.level][self.room][playerState[1][1]][playerState[1][0]] = " " # Removing the tile

                    if not self.crystals[self.level]:
                        self.currentCrystal = True

        if self.playerPositions == [] or self.playerPositions[0] != (self.player.rect.x, self.player.rect.y): # If the player moved
            playerMoved = True

            self.playerPositions.insert(0, (self.player.rect.x, self.player.rect.y)) # inserts at the front of the list
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
                self.gravityDir
            )
        
        self.gravityBeam.update()
    
    
    def render(self, surface):
        super().render()

        # Rendering the player
        self.player.render(surface)

        # Drawing Ellipse and Corlen
        for ent in self.entities:
            ent.render(self.room, self.level, surface)

        # Drawing player
        self.player.render(surface)
    

    def render_grav_beam(self, window):
        # Drawing gravity beam
        for x in range(constants.SCREEN_SIZE[0] // constants.GRAV_BEAM_WIDTH): # Goes through the center of the screen
            # Draws the gravity beam
            self.gravityBeam.render(
                window, 
                (x * constants.GRAV_BEAM_WIDTH, 
                (constants.GRAV_BEAM_TILE_Y_POS * constants.TILE_SIZE[1]) - (self.gravityBeam.images[0].get_height() / 2)) # Centers the beam
            )