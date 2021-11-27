import pygame

import src.scene_base
import src.player
import src.ellipse
import src.utility as utility
import src.constants as constants

class Cutscenes(src.scene_base.SceneBase):
    def __init__(self, tileRenderer):
        super().__init__(__name__)

        self.tileRenderer = tileRenderer
        
        self.room = 0
        self.timer = 0


    def setup(self, scene):
        self.cutsceneData = utility.load_json("data/cutscenes.json")[scene]
        
        self.objects = {}

        for name, position in self.cutsceneData["start"].items():
            if name == "player":
                self.objects[name] = {
                    "obj": src.player.Player(position),
                    "movement": "still"
                }
            
            elif name == "ellipse":
                self.objects[name] = {
                    "obj": src.ellipse.Ellipse(position, 0, 0),
                    "movement": "still"
                }

        levels = utility.load_levels(constants.CUTSCENE_LEVELS_PATH)
        self.level = levels[self.cutsceneData["cutsceneLevel"]]

        self.room = 0

        self.tiles = pygame.Surface((
            constants.SCREEN_TILE_SIZE[0] * constants.TILE_SIZE[0], 
            constants.SCREEN_TILE_SIZE[1] * constants.TILE_SIZE[1]
        ))

        self.tileRenderer.draw_tiles(self.level[self.room], self.tiles)
        self.tileRenderer.setup_room_tile_anims(self.level[self.room])

        # Variables for running commands for cutscenes
        self.timer = 0
        self.runningConditionals = []
        self.activeConditionals = []

    
    def interpret_command(self, command):
        # Interprets a command in the form of [character, command, argument]
        # For example, ["ellipse", "walk", "right"]
        if command[0] in self.objects:
            if command[1] == "walk":
                self.objects[command[0]]["movement"] = command[2]

            elif command[1] == "teleport":
                self.objects[command[0]]["obj"].rect.x = command[2][0]
                self.objects[command[0]]["obj"].rect.y = command[2][1]
        
        elif command[0] == "run": # Runs a conditional
            self.runningConditionals.append(command[1])
        
        elif command[0] == "end":
            return "end"


    def run_conditional(self, condName, conditional):
        checking = self.objects[conditional[0]]["obj"]

        if conditional[1] == "x":
            checking = checking.rect.x
        elif conditional[1] == "y":
            checking = checking.rect.y

        check = eval(f"{checking} {conditional[2]}")
        
        if check:
            self.activeConditionals.append(condName)


    def update(self):
        super().update()

        self.timer += 1

        # Interpretting and running timed commands
        for time, command in self.cutsceneData["time_commands"].items():
            if self.timer == int(time):
                result = self.interpret_command(command)
                if result == "end":
                    return False
        
        # Running conditionals
        for condName in self.runningConditionals:
            self.run_conditional(condName, self.cutsceneData["conditionals"][condName])
        
        # Checking and running commands that are dependent on conditionals
        for conditional, command in self.cutsceneData["cond_commands"].items():
            if conditional in self.activeConditionals:
                self.activeConditionals.remove(conditional)
                result = self.interpret_command(command)
                if result == "end":
                    return False
        
        # Moving objects
        for obj in self.objects:
            object = self.objects[obj]["obj"]
            movement = self.objects[obj]["movement"]

            if movement != "still":
                object.switch_anim("walk")

                if movement == "right":
                    object.rect.x += constants.MAX_SPEED
                    object.facing = 1

                if movement == "left":
                    object.rect.x -= constants.MAX_SPEED
                    object.facing = -1

            else:
                object.switch_anim("idle")
            
            object.update_animation()


    def render(self, window):
        super().render()

        window.blit(self.tiles, (0, 0))
        
        self.objects["player"]["obj"].render(window)

        for obj in self.objects:
            if obj != "player":
                self.objects[obj]["obj"].render(self.room, 0, window)