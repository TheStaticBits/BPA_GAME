import pygame
import logging
import random
import math

import src.player
import src.utility as utility
import src.constants as constants
import src.animation
import src.tile_renderer

class Cutscenes():
    """
    Manages cutscenes. Interprets cutscene commands and
    updates and displays everything to the screen. 
    """
    def __init__(self, removeCutscenes, crystals):
        """Setting up default information and variables"""
        self.logger = logging.getLogger(__name__)

        self.remove_cutscenes = removeCutscenes # Takes a level number and removes numbers with cutscenes
        
        self.crystals = crystals

        self.tileRenderer = src.tile_renderer.TileRenderer()
        
        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        
        self.room = 0
        self.timer = 0

        # Background tiles image
        self.tiles = pygame.Surface(constants.SCREEN_SIZE)

        # Animations used for entities
        self.entitiesAnimList = {
            "corlen": utility.load_animations_dict(constants.CORLEN_ANIMATIONS),
            "ellipse": utility.load_animations_dict(constants.ELLIPSE_ANIMATIONS),

            "belloq": utility.load_animations_dict(constants.BELLOQ_ANIMATIONS)["idle"],
            "bigBite": src.animation.Animation(
                constants.BIG_BITE_DELAY,
                path = constants.BIG_BITE_ANIM_PATH,
                frames = constants.BIG_BITE_TOTAL_FRAMES
            ),
            "redStare": utility.load_animations_dict(constants.RED_STARE_ANIMATIONS)
        }

        # Appended to self.texts when a text is created
        self.defaultText = {
            "text": "",
            "show": False,
            "pos": [0, 0],
            "color": constants.WHITE,
            "displayWaveX": 0,
            "movable": False
        }


    def setup(self, scene, level):
        """Sets up the given level and scene, with all the entities and cutscene data. Also loads the background screen."""
        self.logger.info(f"Setting up cutscene {scene}, at level {level}")

        self.scene = scene
        self.levelNum = level

        # Loading the data for the given cutscene
        self.cutsceneData = utility.load_json("data/cutscenes.json")[scene]
        
        self.objects = {}
        self.tileObjects = {}

        # Iterating through all the starting positions in the cutscene data and creating the corresponding objects
        for name, data in self.cutsceneData["start"].items():
            if name == "player": # Player object
                self.objects[name] = {
                    "obj": src.player.Player(data["pos"]),
                    "facing": "right",
                    "pos": data["pos"],
                    "movement": "still"
                }
            
            elif name in self.entitiesAnimList:
                # Any entities that have animations
                self.objects[name] = {
                    "anim": self.entitiesAnimList[name],
                    "facing": "right",
                    "pos": data["pos"],
                    "room": data["room"],
                    "movement": "still"
                }

                # If there's a dictionary of animations
                if isinstance(self.entitiesAnimList[name], dict):
                    self.objects[name]["playingAnim"] = "idle"
                
            elif data["tile"] in self.tileRenderer.tileAnims:
                # Any tiles that have animations that are needed within the cutscene
                self.tileObjects[name] = {
                    "anim": self.tileRenderer.tileAnims[data["tile"]]["default"].copy(),
                    "pos": data["pos"],
                    "moveTo": data["pos"] # Position to move to
                }
            
            else:
                # Whoops! The given entity doesn't exist.
                self.logger.error(f"Error: Unknown entity {name} in cutscene {self.scene}")
                utility.warning_box(f"Error: Unknown entity {name} in cutscene {self.scene}")
                
        
        # Loading level data
        levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)
        self.level = levels[self.levelNum]
        # Playing the music of the cutscene
        utility.play_music(self.levelData[self.levelNum]["music"])

        # If there's an animation for the background, load it
        if "backgroundAnim" in self.cutsceneData:
            self.backgroundAnim = src.animation.Animation(
                10, 
                path = self.cutsceneData["backgroundAnim"]["path"],
                width = constants.SCREEN_SIZE[0]
            )
        else:
            self.backgroundAnim = None

        self.room = 0

        # Loading tiles in the cutscene
        self.rerender_tiles()

        # For cutscene commands
        self.playerControlled = False
        self.playerCanJump = True

        self.textObject = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE)

        # Will contain dictionaries such as the defaultText dictionary
        # These are created at the command "text create name"
        # Where the "name" will be the key used to access the dictionary in self.texts dictionary
        self.texts = {}

        self.fadeImage = None
        self.fadeProgress = 0
        self.fadeSpeed = 1
        self.fadeDone = False

        # Variables for running commands for cutscenes
        self.timer = 0
        self.runningConditionals = [] # These are conditionals that are being checked every frame
        self.onceConditionals = [] # Conditionals run once
        self.delays = {} 

        self.screenShake = False 
        self.screen = pygame.Surface(constants.SCREEN_SIZE) # Used for screen shaking
    

    def update_crystals(self, crystals):
        """Takes the given parameter and sets self.crystals to it"""
        self.crystals = crystals


    def restart_level(self):
        """Calls the setup command to setup the cutscene again"""
        self.setup(self.scene, self.levelNum)

    
    def rerender_tiles(self):
        """Renders the tiles in the background to a surface that's stored and rendered every frame"""
        self.logger.info("Rendering background tiles")

        self.tiles.fill(constants.BLACK)
        self.tileRenderer.draw_tiles(
            self.level[self.room], self.room,
            self.tiles,
            self.levelData[self.levelNum]["background"]
        )
        self.tileRenderer.setup_room_tile_anims(self.level[self.room])


    def interpret_commands(self, commands):
        """
        Interprets a command in the form of "ellipse walk right" (and others).
        The commands parameter is a list of these commands.
        Some examples of commands are "text create text1" and "delay 50 nextCommand". 
        For full documentation, see data/cutscenes_help.txt
        """
        try:
            for command in commands:
                self.logger.debug(f"Running cutscene command: {command}")

                comm = command.split(" ")

                if comm[0] in self.objects: # If the first element is an entity
                    if comm[1] == "walk": # Walking in that direction
                        self.objects[comm[0]]["movement"] = comm[2]
                    
                    elif comm[1] == "face": # Facing that direction
                        self.objects[comm[0]]["facing"] = comm[2]

                    elif comm[1] == "teleport": # Teleporting to the given x and y coordinates
                        self.objects[comm[0]]["pos"][0] = int(comm[2])
                        self.objects[comm[0]]["pos"][1] = int(comm[3])
                    
                    elif comm[1] == "room": # Setting room number
                        if comm[0] == "player":
                            # Since player's room is the entire cutscene's room, we need to rerender tiles after setting the self.room variable to the given room
                            self.room = int(comm[2])
                            self.rerender_tiles()

                        else:
                            self.objects[comm[0]]["room"] = int(comm[2])
                    
                    elif comm[1] == "controllable":
                        # Player controllable, meaning the user can move the player character now
                        self.playerControlled = True
                        # Updating information in the player object to the data for the entity
                        self.objects["player"]["obj"].rect.x = self.objects[comm[0]]["pos"][0]
                        self.objects["player"]["obj"].rect.y = self.objects[comm[0]]["pos"][1]
                    
                    elif comm[1] == "uncontrollable":
                        # Player cannot be controlled anymore
                        self.playerControlled = False
                        # Resetting velocity
                        self.objects["player"]["obj"].xVelocity = 0
                    
                    elif comm[1] == "jump":
                        # Setting the player's ability to jump
                        self.playerCanJump = (comm[2] == "can")
                
                elif comm[0] in self.tileObjects: # If it's a tile object
                    if comm[1] == "moveTo": # Sets the place the tile should be moving to
                        self.tileObjects[comm[0]]["moveTo"] = (int(comm[2]), int(comm[3]))
                    
                    elif comm[1] == "teleport": # Teleporting the tile to the given x and y coordinates
                        self.tileObjects[comm[0]]["pos"] = [int(comm[2]), int(comm[3])]

                        # Also setting the tile's moveTo position to the x and y if specified
                        if len(comm) == 5 and comm[4] == "moveTo":
                            self.tileObjects[comm[0]]["moveTo"] = (int(comm[2]), int(comm[3]))

                # Text commands
                elif comm[0] == "text":
                    if comm[1] == "create":
                        # Creates a text object in the dictionary from the default text
                        self.texts[comm[2]] = self.defaultText.copy()
                    
                    elif comm[1] == "createMovable":
                        # Creates a text object from the default text, and then also adds a moveTo value and sets the movable value to True
                        self.texts[comm[2]] = self.defaultText.copy()
                        del self.texts[comm[2]]["displayWaveX"]
                        self.texts[comm[2]]["movable"] = True
                        self.texts[comm[2]]["moveTo"] = self.texts[comm[2]]["pos"]
                    
                    else:
                        key = comm[1] # Text key in the text dictionary

                        if comm[2] == "display": # Shows the text
                            self.texts[key]["show"] = True
                        elif comm[2] == "hide": # Hides the text
                            self.texts[key]["show"] = False
                    
                        elif comm[2] == "change": # Changes the text in the text object to the given text
                            self.texts[key]["text"] = " ".join(comm[3:])
                        elif comm[2] == "move": # Teleports the text to the given x and y
                            self.texts[key]["pos"] = [int(comm[3]), int(comm[4])]
                        elif comm[2] == "moveTo": # Text slowly moves towards the given x and y
                            self.texts[key]["moveTo"] = (int(comm[3]), int(comm[4]))
                        elif comm[2] == "color": # Changes text color to the given rgb value
                            self.texts[key]["color"] = (int(comm[3]), int(comm[4]), int(comm[5]))
                

                # The fade command fades an image slowly onto the screen until the transparency is 255
                # Something like: fade speed path_to_image.png
                # Or if it's a solid color: fade speed 255 255 255
                # and for clearing an image: fade clear
                elif comm[0] == "fade":
                    if comm[1] == "clear": # Removes fade image/color
                        self.fadeImage = None
                    
                    else:
                        if len(comm) == 3: # If it gives an image
                            # Loading image given
                            self.fadeImage = pygame.image.load(comm[2]).convert_alpha()
                        
                        elif len(comm) == 5: # If it gives a solid color
                            # Creates an image filled with purely the color given
                            self.fadeImage = pygame.Surface(constants.SCREEN_SIZE)
                            self.fadeImage.fill((int(comm[2]), int(comm[3]), int(comm[4])))
                        
                        # Resetting the fade progress and "done"
                        self.fadeProgress = 0
                        self.fadeSpeed = int(comm[1]) # Fade speed
                        self.fadeDone = False
                
                
                elif comm[0] == "shake": # Starting/ending screen shake
                    self.screenShake = (comm[1] == "start")
                
                elif comm[0] == "run": # Runs a conditional
                    self.runningConditionals.append(comm[1])
                    
                    if "once" in comm: # Runs once
                        self.onceConditionals.append(comm[1])
                
                elif comm[0] == "music": # Starts the music given
                    utility.play_music(comm[1])
                
                elif comm[0] == "delay": # Starts a delay
                    self.delays[comm[2]] = int(comm[1])
                
                elif comm[0] in ("end", "restart"): # Ends/restarts
                    return comm[0]

        except Exception as exc:
            # Oh no! An error occured while running the command!
            # Logs and creates a warning box
            self.logger.error(f"Error occured in cutscene command: {command}\Error: {exc}")
            utility.warning_box(f"Error occured in cutscene command: {command}\Error: {exc}")


    def run_conditional(self, conditional) -> bool:
        """Runs the given conditional, returning the result"""

        multConditionals = conditional.split(" and ")
        if len(multConditionals) == 1:
            cond = conditional.split(" ")

            # If the command is asking for the data of an entity
            if len(cond) == 4:
                if cond[1] == "x":
                    checking = self.objects[cond[0]]["pos"][0]
                elif cond[1] == "y":
                    checking = self.objects[cond[0]]["pos"][1]
                
                elif cond[1] == "room":
                    checking = self.objects[cond[0]]["room"]
                
                command = " ".join(cond[2:])

                return eval(f"{checking} {command}")
            
            if cond[0] == "room":
                return eval(f"{self.room} {cond[1]} {cond[2]}")
                
            elif cond == ["fade", "done"]:
                return self.fadeDone
            
            elif cond[0] == "crystals":
                levelWithoutCutscenes = self.remove_cutscenes(self.levelNum)

                result = True
                for x in range(levelWithoutCutscenes):
                    if not self.crystals[x]:
                        result = False
                        break
                
                command = " ".join(cond[1:])

                return eval(f"{result} {command}")
            
            else:
                self.logger.error(f"Unknown cutscene conditional {conditional}")
                utility.warning_box(f"Unknown cutscene conditional {conditional}")
                return False

        else:
            # Goes through and runs all conditionals in the list
            for c in multConditionals:
                if not self.run_conditional(c):
                    return False
            
            return True
    

    def get_anim_obj(self, name, data) -> "src.animation.Animation":
        """Gets the animation object for the given name and data object based on the name of the thing being asked for"""
        if name == "player":
            return data["obj"].animations[data["obj"].currentAnim]
        elif name == "redStare":
            return data["anim"]["body"]
        elif "playingAnim" in data:
            return data["anim"][data["playingAnim"]]
        else:
            return data["anim"]
    

    def move(self, position, moveTo, speed) -> list:
        """Moves the given position towards the moveTo position at the given speed"""
        if utility.distance_to(position, moveTo) < 1:
            return list(moveTo)
        
        degrees = utility.angle_to(position, moveTo)
        
        position[0] += math.cos(degrees) * speed
        position[1] += math.sin(degrees) * speed

        return position



    def update(self, window):
        """Updates everything within the cutscene, running commands, updating entities and animations, etc."""
        inputs = window.inputs

        self.tileRenderer.update_tiles_with_anims()

        commandsToBeRun = []

        # Updating background animation if it's on the provided room
        if self.backgroundAnim is not None:
            if self.room == self.cutsceneData["backgroundAnim"]["room"]:
                self.backgroundAnim.update()

        # Interpretting and running timed commands
        for time, commands in self.cutsceneData["time_commands"].items():
            if self.timer == int(time):
                commandsToBeRun.append(commands)
        
        # Running conditionals
        for condName in self.runningConditionals:
            if self.run_conditional(self.cutsceneData["conditionals"][condName]):
                # If the conditional was successful, add to the list of commands to be run
                self.runningConditionals.remove(condName)
                commandsToBeRun.append(self.cutsceneData["cond_commands"][condName])
            
            elif condName in self.onceConditionals:
                # If the conditional failed but was set to run once, remove it from the lists
                self.runningConditionals.remove(condName)
                self.onceConditionals.remove(condName)
        
        # Updating delays
        for delayName in list(self.delays):
            if self.delays[delayName] == 0 or inputs["enter"]:
                # If the delay finished or the user pressed enter to skip it, remove it from the list and add it to the commands to be run
                del self.delays[delayName]
                commandsToBeRun.append(self.cutsceneData["cond_commands"][delayName])

            else:
                self.delays[delayName] -= 1 # Decrementing the delay

        # Running commands in the commands to be run
        for command in commandsToBeRun:
            result = self.interpret_commands(command)
            if result is not None:
                return result
        
        # Updating player's animation if not using player object class
        if not self.playerControlled:
            self.objects["player"]["obj"].update_animation()

        # Moving and updating objects
        for name, dat in self.objects.items():
            # Updating animations of the objects
            if name != "player":
                if name == "redStare":
                    dat["anim"]["body"].update()
                    dat["anim"]["mouth"].update()
                elif "playingAnim" in dat:
                    dat["anim"][dat["playingAnim"]].update()
                else:
                    dat["anim"].update()

            elif name == "player" and self.playerControlled:
                if not self.playerCanJump: # Setting up button to false if the player isn't allowed to jump
                    inputs["up"] = False

                # Updating player
                result = dat["obj"].update(
                    self.level[self.room], 
                    self.room,
                    self.level,
                    inputs
                )

                if result == "right": # If the player moved to the right side of the screen
                    self.logger.info("Player walked to the next room")
                    dat["obj"].rect.x -= constants.SCREEN_SIZE[0] # Moving to the left side of the screen
                    self.room += 1 # Incrementing the room number

                    if self.room >= len(self.level): # If the room is the last room
                        self.logger.info("Player walked off cutscene")
                        return "end"
                    else:
                        # Rerending tiles for the background
                        self.rerender_tiles()
                        
                
                elif result == "left": # If the player moved to the left side of the screen
                    if self.room > 0: # If the room is not the first room
                        self.logger.info("Player walked back a room")
                        dat["obj"].rect.x += constants.SCREEN_SIZE[0] # Moving to the right side of the screen
                        self.room -= 1
                        self.rerender_tiles() # Rerending tiles for the background
                
                # Setting the data for the position to the player's current actual position
                dat["pos"] = dat["obj"].rect.topleft

                continue # Skipping the rest (movement for normal objects)

            if dat["movement"] != "still": # Movement isn't still
                # Changing animation to the new animation if it isn't already playing
                if "playingAnim" in dat and name != "redStare":
                    if dat["playingAnim"] != "walk":
                        dat["anim"]["walk"].reset()
                        dat["playingAnim"] = "walk"
                elif name == "player":
                    dat["obj"].switch_anim("walk")
                
                # Getting width
                width = self.get_anim_obj(name, dat).get_image_width()

                if dat["movement"] == "right": # If the movement was moving right
                    # Moving right
                    dat["pos"][0] += constants.MAX_SPEED
                    dat["facing"] = "right" # Setting direction facing to right
                    
                    # If the object moved off the screen on the right
                    if dat["pos"][0] >= (constants.SCREEN_SIZE[0]):
                        self.logger.info(f"Entity {name} walked into the next room")

                        dat["pos"][0] = -width # Moving to left side of the screen (offscreen)

                        if name == "player": # If the entity was the player,
                            # Increment cutscene rooom and rerender tiles if the room is not the last room
                            self.room += 1
                            if self.room == len(self.level):
                                return "end" # Reached the end, ending the cutscene
                            else:
                                # Updating background tiles to the new room
                                self.rerender_tiles()
                        
                        else: # Normal entity
                            # Adding one to the room number of the entity
                            dat["room"] += 1

                elif dat["movement"] == "left":
                    # Moving entity left
                    dat["pos"][0] -= constants.MAX_SPEED
                    dat["facing"] = "left"

                    # If the object was off the screen on the left side
                    if dat["pos"][0] <= -width:
                        self.logger.info(f"Entity {name} walked into the previous room")

                        # If it was the player
                        if name == "player":
                            if self.room > 0: # If the room is not the first room
                                # Decrement the room number and rerender tiles
                                self.room -= 1
                                self.rerender_tiles()
                        
                        else:
                            # Normal entity, change its room number
                            dat["room"] -= 1
                        
                        # Moving to the right side of the screen in the new room
                        dat["pos"][0] += constants.SCREEN_SIZE[0]


            else:
                # If there was no movement, reset the animation to idle (if it wasn't already idle, reset it as well)
                if "playingAnim" in dat and name != "redStare":
                    if dat["playingAnim"] != "idle":
                        dat["anim"]["idle"].reset()
                        dat["playingAnim"] = "idle"
                elif name == "player": 
                    # Changing player object animation
                    dat["obj"].switch_anim("idle")
        
        # Moving and updating tile objects
        for t in self.tileObjects.values():
            t["anim"].update()

            if t["pos"] != t["moveTo"]: # If the object isn't at its destination
                # Moving the object towards its destination
                t["pos"] = self.move(t["pos"], t["moveTo"], 2)
        
        # Moving text that is movable
        for text in self.texts.values():
            if text["movable"]: # If it's movable text
                if text["pos"] != text["moveTo"]: # Not at its destination
                    # Moving the text towards its destination
                    text["pos"] = self.move(text["pos"], text["moveTo"], 0.3)
            
        self.timer += 1 # Incrementing timer (for time commands)


    def render(self, window):
        """Renders everything within the cutscene, including the background/tiles, objects, and text"""
        # Tiles
        self.screen.blit(self.tiles, (0, 0))
        # Tiles with animations
        self.tileRenderer.render_tiles_with_anims(self.screen, 1, constants.SCREEN_TILE_SIZE[1])

        # Rendering background animation if there is one and it's on the room that it was set on
        if self.backgroundAnim is not None:
            if self.room == self.cutsceneData["backgroundAnim"]["room"]:
                self.backgroundAnim.render(self.screen, (0, 0))
        
        # Rendering objects
        for name, dat in self.objects.items():
            # If the object is the player and the player is not being controlled by the user, or it's not the player
            if name == "player" and not self.playerControlled or name != "player":
                # If it's the player (which is always on screen) or the room of the object is the current room as well
                if name == "player" or dat["room"] == self.room:
                    if name != "redStare": # If it's not the Red Stare (who has two things to render)
                        # Gets the frame of the animation of the object
                        image = self.get_anim_obj(name, dat).get_frame()
                        
                        # Flips the frame based on the direction the object is facing
                        image = pygame.transform.flip(image, dat["facing"] == "left", False)
                        # Drawing at position
                        self.screen.blit(image, dat["pos"])
                    
                    else:
                        # Rendering body and mouth at offset of the Red Stare
                        dat["anim"]["body"].render(self.screen, dat["pos"])
                        dat["anim"]["mouth"].render(
                            self.screen, 
                            (dat["pos"][0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                             dat["pos"][1] + constants.RED_STARE_MOUTH_OFFSET[1])
                        )
            
            else:
                # Rendering the player object
                self.objects["player"]["obj"].render(self.screen)
        
        # Rendering tile objects
        for dat in self.tileObjects.values():
            dat["anim"].render(self.screen, dat["pos"])

        if self.screenShake:
            # Creating a random offset for the entire screen
            offset = (
                random.randint(-constants.SCREEN_SHAKE_POWER, constants.SCREEN_SHAKE_POWER),
                random.randint(-constants.SCREEN_SHAKE_POWER, constants.SCREEN_SHAKE_POWER)
            )

            # Drawing the rendered screen to the window at the screen shake offset
            window.blit(self.screen, offset)
        
        else:
            # Drawing at the top left
            window.blit(self.screen, (0, 0))
        
        # Drawing screen shadow
        window.blit(self.screenShadow, (0, 0))

        # Drawing the fade image to the screen if there is one
        if self.fadeImage is not None:
            if not self.fadeDone:
                # Updating fade alpha
                self.fadeProgress += self.fadeSpeed

                if self.fadeProgress >= 255: # 255 is full ocpacity
                    # Fade is done
                    self.fadeDone = True
            
            # Drawing the fade image with the current alpha value
            self.fadeImage.set_alpha(self.fadeProgress)
            window.blit(self.fadeImage, (0, 0))
        
        # Going through all text objects and rendering them with borders at their positions
        for text in self.texts.values():
            if text["show"]: # If the text is to be displayed
                if not text["movable"]: # If the text isn't movable text
                    # Adding to the sine wave counter
                    text["displayWaveX"] += 0.05
                    # Using the sine wave counter to get the new position of the text
                    # (For bobbing up and down)
                    textYOffset = math.sin(text["displayWaveX"]) * 5
                
                else: # Otherwise, set it to zero
                    # (Movable text doesn't bob up/down)
                    textYOffset = 0

                fullText = text["text"].split("\n")

                # Going through all rows of the text
                for count, t in enumerate(fullText):
                    # Getting text surface
                    renderText = self.textObject.render(t, False, text["color"])

                    # Getting position, centering it on the x position and moving it down by the y if there are multiple lines
                    position = (text["pos"][0] - renderText.get_width() / 2, text["pos"][1] + textYOffset + count * 12)

                    # Drawing the text 
                    utility.draw_text_with_border(window, position, t, self.textObject, text["color"], renderText = renderText)