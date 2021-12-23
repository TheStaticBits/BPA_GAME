import pygame
import random
import math

import src.scene_base
import src.player
import src.utility as utility
import src.constants as constants
import src.animation
import src.tile_renderer

class Cutscenes(src.scene_base.SceneBase):
    def __init__(self, removeCutscenes, crystals):
        super().__init__(__name__)

        self.remove_cutscenes = removeCutscenes # Takes a level number and removes numbers with cutscenes
        
        self.crystals = crystals

        self.tileRenderer = src.tile_renderer.TileRenderer()
        
        self.screenShadow = pygame.image.load(constants.SCREEN_SHADOW_PATH).convert_alpha()
        
        self.room = 0
        self.timer = 0

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


    def setup(self, scene, level):
        self.scene = scene
        self.levelNum = level

        self.cutsceneData = utility.load_json("data/cutscenes.json")[scene]
        
        self.objects = {}
        self.tileObjects = {}

        for name, data in self.cutsceneData["start"].items():
            if name == "player":
                self.objects[name] = {
                    "obj": src.player.Player(data["pos"]),
                    "facing": "right",
                    "pos": data["pos"],
                    "movement": "still"
                }
            
            elif name in self.entitiesAnimList:
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
                self.tileObjects[name] = {
                    "anim": self.tileRenderer.tileAnims[data["tile"]]["default"].copy(),
                    "pos": data["pos"],
                    "moveTo": data["pos"]
                }
            
            else:
                raise Exception(f"Error: Unknown entity {name}")
                

        levels, self.levelData = utility.load_levels(constants.LEVELS_PATH)
        self.level = levels[self.levelNum]
        utility.play_music(self.levelData[self.levelNum]["music"])

        if "backgroundAnim" in self.cutsceneData:
            self.backgroundAnim = src.animation.Animation(
                10, 
                path = self.cutsceneData["backgroundAnim"]["path"],
                width = constants.SCREEN_SIZE[0]
            )
        
        else:
            self.backgroundAnim = None

        self.room = 0

        self.tiles = pygame.Surface((
            constants.SCREEN_SIZE[0], 
            constants.SCREEN_SIZE[1]
        ))

        self.playerControlled = False
        self.playerCanJump = True

        self.rerender_tiles()

        self.textObject = pygame.font.Font(constants.FONT_PATH, constants.FONT_SIZE)

        # Will contain dictionaries such as the defaultText dictionary
        # These are created at the command "text create name"
        # Where the "name" will be the key used to access the dictionary in self.texts dictionary
        self.texts = {}

        self.defaultText = {
            "text": "",
            "show": False,
            "position": (0, 0),
            "color": constants.WHITE,
            "displayWaveX": 0
        }

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
        self.crystals = crystals


    def restart_level(self):
        self.setup(self.scene, self.levelNum)

    
    def rerender_tiles(self):
        self.tiles.fill(constants.BLACK)
        self.tileRenderer.draw_tiles(
            self.level[self.room], 
            self.tiles, 
            self.levelData[self.levelNum]["background"]    
        )
        self.tileRenderer.setup_room_tile_anims(self.level[self.room])


    def interpret_commands(self, commands):
        # Interprets a command in the form of "ellipse walk right" (and others)
        # The commands parameter is a list of these commands
        # LOok inside data/cutscenes.json for more examples
        try:
            for command in commands:
                comm = command.split(" ")

                if comm[0] in self.objects:
                    if comm[1] == "walk":
                        self.objects[comm[0]]["movement"] = comm[2]
                    
                    elif comm[1] == "face":
                        self.objects[comm[0]]["facing"] = comm[2]

                    elif comm[1] == "teleport":
                        self.objects[comm[0]]["pos"][0] = int(comm[2])
                        self.objects[comm[0]]["pos"][1] = int(comm[3])
                    
                    elif comm[1] == "room":
                        self.objects[comm[0]]["room"] = int(comm[2])
                    
                    elif comm[1] == "controllable":
                        self.playerControlled = True
                        self.objects["player"]["obj"].rect.x = self.objects[comm[0]]["pos"][0]
                        self.objects["player"]["obj"].rect.y = self.objects[comm[0]]["pos"][1]
                    
                    elif comm[1] == "uncontrollable":
                        self.playerControlled = False
                        self.objects["player"]["obj"].xVelocity = 0
                    
                    elif comm[1] == "jump":
                        self.playerCanJump = (comm[2] == "can")
                
                elif comm[0] in self.tileObjects:
                    if comm[1] == "moveTo":
                        self.tileObjects[comm[0]]["moveTo"] = (int(comm[2]), int(comm[3]))
                    
                    elif comm[1] == "teleport":
                        self.tileObjects[comm[0]]["pos"] = [int(comm[2]), int(comm[3])]

                        if len(comm) == 5 and comm[4] == "moveTo":
                            self.tileObjects[comm[0]]["moveTo"] = (int(comm[2]), int(comm[3]))

                elif comm[0] == "text":
                    if comm[1] == "create":
                        self.texts[comm[2]] = self.defaultText.copy()
                    
                    else:
                        key = comm[1]

                        if comm[2] == "display":
                            self.texts[key]["show"] = True
                        elif comm[2] == "hide":
                            self.texts[key]["show"] = False
                    
                        elif comm[2] == "change":
                            self.texts[key]["text"] = " ".join(comm[3:])
                        elif comm[2] == "move":
                            self.texts[key]["position"] = (int(comm[3]), int(comm[4])) 
                        elif comm[2] == "color":
                            self.texts[key]["color"] = (int(comm[3]), int(comm[4]), int(comm[5]))
                

                # The fade command fades an image slowly onto the screen until the transparency is 255
                # Something like: fade speed path_to_image.png
                # Or if it's a solid color: fade speed 255 255 255
                # and for clearing an image: fade clear
                elif comm[0] == "fade":
                    if comm[1] == "clear":
                        self.fadeImage = None
                    
                    else:
                        if len(comm) == 3: # If it gives an image
                            self.fadeImage = pygame.image.load(comm[2]).convert_alpha()
                        
                        elif len(comm) == 5: # If it gives a solid color
                            rect = pygame.Rect(0, 0, constants.SCREEN_SIZE[0], constants.SCREEN_SIZE[1])
                            self.fadeImage = pygame.Surface(constants.SCREEN_SIZE)
                            pygame.draw.rect(self.fadeImage, (int(comm[2]), int(comm[3]), int(comm[4])), rect)
                        
                        self.fadeProgress = 0
                        self.fadeSpeed = int(comm[1])
                        self.fadeDone = False
                
                
                elif comm[0] == "shake":
                    self.screenShake = (comm[1] == "start")
                
                elif comm[0] == "run": # Runs a conditional
                    self.runningConditionals.append(comm[1])
                    
                    if "once" in comm:
                        self.onceConditionals.append(comm[1])
                
                elif comm[0] == "music":
                    utility.play_music(comm[1])
                
                elif comm[0] == "delay": # Starts a delay
                    self.delays[comm[2]] = int(comm[1])
                
                elif comm[0] in ("end", "restart"):
                    return comm[0]

        except Exception as exc:
            raise Exception(f"Error occured in cutscene command: {command}\nCommand: {exc}")


    def run_conditional(self, conditional):
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
                print("Error: Unknown conditional")
                print(conditional)

        else:
            # Goes through and runs all conditionals in the list
            for c in multConditionals:
                if not self.run_conditional(c):
                    return False
            
            return True
    

    def get_anim_obj(self, name, data) -> "src.animation.Animation":
        if name == "player":
            return data["obj"].animations[data["obj"].currentAnim]
        elif name == "redStare":
            return data["anim"]["body"]
        elif "playingAnim" in data:
            return data["anim"][data["playingAnim"]]
        else:
            return data["anim"]


    def update(self, window):
        super().update()

        inputs = window.inputs

        commandsToBeRun = []

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
                self.runningConditionals.remove(condName)
                commandsToBeRun.append(self.cutsceneData["cond_commands"][condName])
            
            elif condName in self.onceConditionals:
                self.runningConditionals.remove(condName)
                self.onceConditionals.remove(condName)
        
        # Updating delays
        for delayName in list(self.delays):
            if self.delays[delayName] == 0 or inputs["enter"]:
                del self.delays[delayName]
                commandsToBeRun.append(self.cutsceneData["cond_commands"][delayName])

            else:
                self.delays[delayName] -= 1

        # Running commands
        for command in commandsToBeRun:
            result = self.interpret_commands(command)
            if result is not None:
                return result
        
        # Updating player animation
        self.objects["player"]["obj"].update_animation()

        # Moving objects
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
                if not self.playerCanJump:
                    inputs["up"] = False

                result = dat["obj"].update(
                    self.level[self.room], 
                    self.room,
                    self.level,
                    inputs
                )

                if result == "right":
                    dat["obj"].rect.x -= constants.SCREEN_SIZE[0]
                    self.room += 1

                    if self.room == len(self.level):
                        return "end"
                    else:
                        self.rerender_tiles()
                        
                
                elif result == "left":
                    if self.room > 0:
                        dat["obj"].rect.x += constants.SCREEN_SIZE[0]
                        self.room -= 1
                        self.rerender_tiles()
                
                
                dat["pos"] = dat["obj"].rect.topleft


            if dat["movement"] != "still":
                if "playingAnim" in dat and name != "redStare":
                    if dat["playingAnim"] != "walk":
                        dat["anim"]["walk"].reset()
                        dat["playingAnim"] = "walk"
                elif name == "player":
                    dat["obj"].switch_anim("walk")
                
                width = self.get_anim_obj(name, dat).get_image_width()

                if dat["movement"] == "right":
                    dat["pos"][0] += constants.MAX_SPEED
                    dat["facing"] = "right"
                    
                    if dat["pos"][0] >= (constants.SCREEN_SIZE[0]):
                        dat["pos"][0] = -width

                        if name == "player":
                            self.room += 1
                            if self.room == len(self.level):
                                return "end"
                            else:
                                self.rerender_tiles()
                        
                        else:
                            dat["room"] += 1

                elif dat["movement"] == "left":
                    dat["pos"][0] -= constants.MAX_SPEED
                    dat["facing"] = "left"

                    if dat["pos"][0] <= -width:
                        if name == "player":
                            if self.room > 0:
                                self.room -= 1
                                self.rerender_tiles()
                        
                        else:
                            dat["room"] -= 1
                        
                        dat["pos"][0] += constants.SCREEN_SIZE[0]


            else:
                if "playingAnim" in dat and name != "redStare":
                    if dat["playingAnim"] != "idle":
                        dat["anim"]["idle"].reset()
                        dat["playingAnim"] = "idle"
                elif name == "player":
                    dat["obj"].switch_anim("idle")
        
        # Moving and updating tile objects
        for t in self.tileObjects.values():
            t["anim"].update()

            if t["pos"] != t["moveTo"]:
                degrees = utility.angle_to(t["pos"], t["moveTo"])
                
                t["pos"][0] += math.cos(degrees) * 2
                t["pos"][1] += math.sin(degrees) * 2

                if utility.distance_to(t["pos"], t["moveTo"]) < 1:
                    t["pos"] = t["moveTo"]
            
        self.timer += 1


    def render(self, window):
        super().render()

        self.screen.blit(self.tiles, (0, 0))

        if self.backgroundAnim is not None:
            if self.room == self.cutsceneData["backgroundAnim"]["room"]:
                self.backgroundAnim.render(self.screen, (0, 0))
        
        for name, dat in self.objects.items():
            if name == "player" and not self.playerControlled or name != "player":
                if name == "player" or dat["room"] == self.room:
                    if name != "redStare":
                        image = self.get_anim_obj(name, dat).get_frame()
                        
                        image = pygame.transform.flip(image, dat["facing"] == "left", False)

                        self.screen.blit(image, dat["pos"])
                    
                    else:
                        dat["anim"]["body"].render(self.screen, dat["pos"])
                        dat["anim"]["mouth"].render(
                            self.screen, 
                            (dat["pos"][0] + constants.RED_STARE_MOUTH_OFFSET[0], 
                             dat["pos"][1] + constants.RED_STARE_MOUTH_OFFSET[1])
                        )
            
            else:    
                self.objects["player"]["obj"].render(self.screen)

        
        for dat in self.tileObjects.values():
            dat["anim"].render(self.screen, dat["pos"])

        if self.fadeImage is not None:
            if not self.fadeDone:
                self.fadeProgress += self.fadeSpeed

                if self.fadeProgress >= 255:
                    self.fadeDone = True
            
            self.fadeImage.set_alpha(self.fadeProgress)
            self.screen.blit(self.fadeImage, (0, 0))
        

        # Going through all text objects and rendering them
        for text in self.texts.values():
            if text["show"]:
                text["displayWaveX"] += 0.05

                textYOffset = math.sin(text["displayWaveX"]) * 5
                fullText = text["text"].split("\n")

                for count, t in enumerate(fullText):
                    renderText = self.textObject.render(t, False, text["color"])

                    position = (text["position"][0] - renderText.get_width() / 2, text["position"][1] + textYOffset + count * 12)

                    utility.draw_text_with_border(self.screen, position, t, self.textObject, text["color"], renderText = renderText)
        

        if self.screenShake:
            offset = (
                random.randint(-constants.SCREEN_SHAKE_POWER, constants.SCREEN_SHAKE_POWER),
                random.randint(-constants.SCREEN_SHAKE_POWER, constants.SCREEN_SHAKE_POWER)
            )

            window.blit(self.screen, offset)
        
        else:
            window.blit(self.screen, (0, 0))
        
        window.blit(self.screenShadow, (0, 0))