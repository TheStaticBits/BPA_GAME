import pygame

class Level:
    def __init__(self, level, room):
        self.room = room
        self.level = level
    
        with open("levels.txt", "r") as file:
            data = file.read()
        
        #print(data)
        
        data = data.split("\n[``````]\n") # splits by level
        
        print(data)

        for item in data:
            print(item.split("\n```\n"), "    1")
        
        data = [item.split("\n```\n") for item in data] # splits by room

        print(data)

        for item in data:
            print(item.split("\n"))

        data = [item.split("\n") for item in data] # splits by row 
        self.data = [list(item) for item in data] # splits by tile
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
        some interpreting needs to happen here to know what type of wall needs to be placed
        """

        print(self.data)



    def render(self, tileSize, level, activeRoom):
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

level = Level(1, 2)
Level.render(1, 0, 0)