import pygame

class Level:
    def __init__(self, level, room):
        self.room = room
        self.level = level
    
        with open("levels.txt", "r") as file:
            data = file.read()

        self.data = data.split("\n[``````]\n") # splits by level

        for level in self.data:
            level = level.split("\n```\n") # splits by room

            for room in level:
                room = room.split("\n") # splits by row 

                for row in room:
                    row = list(row) # splits by tile
        
        # at this point, data is a list of lists (levels) of lists (rooms) of lists (rows) of lists (tiles)
        
        """
        self.drawTiles = {
            "w": {
                "left": pygame.image.load("res/wall_l.png").convert_alpha()
                "right": pygame.image.load("res/wall_r.png").convert_alpha()
                "up": pygame.image.load("res/wall_u.png").convert_alpha()
                "down": pygame.image.load("res/wall_d.png").convert_alpha() # the four different variations of the wall sprite (up down left right)
            },
            "f": pygame.image.load("res/flag.png").convert_alpha()
        }
        
        0 = 0/1 uses on a ring
        1 = 1/1
        2 = 0/2
        3 = 1/2
        4 = 2/2
        5 = 0/3
        6 = 1/3
        7 = 2/3
        8 = 3/3
        so the numbers you will put in the levels.txt file to represent an orb are
        1, 4, 8
        some interpreting needs to happen here to know what type of wall needs to be placed
        """

        print(self.data)

    #def interpret_direction(self, tilePosition, ):

    def render(self, window, tileSize, level, activeRoom):
        reader = {
            "x": 0,
            "y": 0
        }
        

        for y in range(len(self.data[level][activeRoom])):
            for x in range(len(self.data[level][activeRoom][y])):
                letter = self.data[level][activeRoom][y][x]
                print(letter)
                if self.data[level][activeRoom][y][x] != " ":
                    pass
                if self.data[level][activeRoom][y][x] == "w":
                    pass # WE NEED AN INTERPRETER HERE!

level = Level(1, 2)
level.render(1, 0, 0)