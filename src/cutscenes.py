import pygame
import math

import src.scene_base
import src.player
import src.ellipse_and_corlen as eac
import src.utility as utility
import src.constants as constants
import src.animation
import src.tile_renderer

class Cutscenes(src.scene_base.SceneBase):
    def __init__(self):
        super().__init__(__name__)

        self.tileRenderer = src.tile_renderer.TileRenderer()
        
        self.room = 0
        self.timer = 0


    def setup(self, scene, level):
        self.scene = scene
        self.levelNum = level

        self.cutsceneData = utility.load_json("data/cutscenes.json")[scene]
        
        self.objects = {}

        for name, position in self.cutsceneData["start"].items():
            if name == "player":
                self.objects[name] = {
                    "obj": src.player.Player(position["pos"]),
                    "movement": "still"
                }
            
            elif name == "ellipse":
                self.objects[name] = {
                    "obj": eac.create_entity("ellipse", position["pos"], position["room"], 0), # Since each cutscene is one level, the level number doesn't matter
                    "movement": "still"
                }
            
            elif name == "corlen":
                self.objects[name] = {
                    "obj": eac.create_entity("corlen", position["pos"], position["room"], 0),
                    "movement": "still"
                }

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

        # Variables for running commands for cutscenes
        self.timer = 0
        self.runningConditionals = [] # These are conditionals that are being checked every frame
        self.delays = {} 


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
                        if comm[2] == "right":
                            self.objects[comm[0]]["obj"].facing = 1
                        else:
                            self.objects[comm[0]]["obj"].facing = -1

                    elif comm[1] == "teleport":
                        self.objects[comm[0]]["obj"].rect.x = int(comm[2])
                        self.objects[comm[0]]["obj"].rect.y = int(comm[3])
                    
                    elif comm[1] == "controlled":
                        self.playerControlled = True
                    
                    elif comm[1] == "uncontrolled":
                        self.playerControlled = False
                        self.objects["player"]["obj"].xVelocity = 0
                    
                    elif comm[1] == "jump":
                        if comm[2] == "can":
                            self.playerCanJump = True
                        else:
                            self.playerCanJump = False

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
                
                elif comm[0] == "run": # Runs a conditional
                    self.runningConditionals.append(comm[1])
                
                elif comm[0] == "delay": # Starts a delay
                    self.delays[comm[2]] = int(comm[1])
                
                elif comm[0] == "end":
                    return "end"

        except Exception as exc:
            raise Exception(f"Error occured in command: {command}\nCommand: {exc}")


    def run_conditional(self, conditional):
        multConditionals = conditional.split(" and ")
        if len(multConditionals) == 1:
            cond = conditional.split(" ")

            # If the command is asking for the data of an entity
            if len(cond) == 4:
                checking = self.objects[cond[0]]["obj"]

                if cond[1] == "x":
                    checking = checking.rect.x
                elif cond[1] == "y":
                    checking = checking.rect.y
                
                elif cond[1] == "room":
                    checking = checking.room
                
                command = "".join(cond[2:])

                check = eval(f"{checking} {command}")
            
            # if the command is asking for a single variable
            elif len(cond) == 3:
                if cond[0] == "room":
                    check = eval(f"{self.room} {cond[1]} {cond[2]}")
            
            if check:
                return True

            return False

        else:
            # Goes through and runs all conditionals in the list
            for c in multConditionals:
                if not self.run_conditional(c):
                    return False
            
            return True


    def update(self, window):
        super().update()

        inputs = window.inputs

        if self.backgroundAnim is not None:
            if self.room == self.cutsceneData["backgroundAnim"]["room"]:
                self.backgroundAnim.update()

        # Interpretting and running timed commands
        for time, commands in self.cutsceneData["time_commands"].items():
            if self.timer == int(time):
                result = self.interpret_commands(commands)
                if result == "end":
                    return "end"
        
        # Running conditionals
        for condName in self.runningConditionals:
            if self.run_conditional(self.cutsceneData["conditionals"][condName]):
                self.runningConditionals.remove(condName)
                
                result = self.interpret_commands(self.cutsceneData["cond_commands"][condName])
                if result == "end":
                    return "end"
        
        # Updating delays
        for delayName in list(self.delays):
            if self.delays[delayName] == 0:
                del self.delays[delayName]
                self.interpret_commands(self.cutsceneData["cond_commands"][delayName])

            else:
                self.delays[delayName] -= 1
        
        # Moving objects
        for obj in self.objects:
            object = self.objects[obj]["obj"]
            movement = self.objects[obj]["movement"]

            if obj == "player" and self.playerControlled:
                if not self.playerCanJump:
                    inputs["up"] = False

                result = object.update(
                    self.level[self.room], 
                    self.room,
                    self.level,
                    inputs
                )

                if result == "right":
                    try:
                        object.rect.x -= constants.SCREEN_SIZE[0]
                        self.room += 1
                        self.rerender_tiles()

                    except IndexError:
                        # Once the player has reached the end of the level, the cutscene ends
                        return "end"
                
                elif result == "left":
                    if self.room > 0:
                        object.rect.x += constants.SCREEN_SIZE[0]
                        self.room -= 1
                        self.rerender_tiles()
                
                continue


            if movement != "still":
                object.switch_anim("walk")

                if movement == "right":
                    object.rect.x += constants.MAX_SPEED
                    object.facing = 1
                    
                    if object.rect.x >= (constants.SCREEN_SIZE[0]):
                        if obj == "player":
                            try:
                                object.rect.x = -constants.PLAYER_WIDTH
                                self.room += 1
                                self.rerender_tiles()

                            except IndexError:
                                return "end"
                        
                        else:
                            object.rect.x = -object.rect.width
                            object.room += 1

                if movement == "left":
                    object.rect.x -= constants.MAX_SPEED
                    object.facing = -1

                    if object.rect.x <= -object.rect.width:
                        if obj == "player":
                            if self.room > 0:
                                self.room -= 1
                                self.rerender_tiles()
                        
                        else:
                            object.room -= 1
                        
                        object.rect.x += constants.SCREEN_SIZE[0]


            else:
                object.switch_anim("idle")
            
            object.update_animation()
            
        self.timer += 1


    def render(self, window):
        super().render()

        window.blit(self.tiles, (0, 0))

        if self.backgroundAnim is not None:
            if self.room == self.cutsceneData["backgroundAnim"]["room"]:
                self.backgroundAnim.render(window, (0, 0))
        
        self.objects["player"]["obj"].render(window)

        for obj in self.objects:
            if obj != "player":
                self.objects[obj]["obj"].render_with_check(self.room, 0, window)
        

        # Going through all text objects and rendering them
        for text in self.texts.values():
            if text["show"]:
                text["displayWaveX"] += 0.05

                textYOffset = math.sin(text["displayWaveX"]) * 5
                fullText = text["text"].split("\n")

                for count, t in enumerate(fullText):
                    renderText = self.textObject.render(t, False, text["color"])

                    position = (text["position"][0] - renderText.get_width() / 2, text["position"][1] + textYOffset + count * 12)

                    utility.draw_text_with_border(window, position, t, self.textObject, text["color"], renderText = renderText)