import pygame
import src.constants

class Window:
    WINDOW_SIZE = (
        src.constants.PX_SCALE_FACTOR * src.constants.TILE_SIZE[0] * src.constants.SCREEN_TILE_SIZE[0], 
        src.constants.PX_SCALE_FACTOR * src.constants.TILE_SIZE[1] * src.constants.SCREEN_TILE_SIZE[1]
    ) # This is the size of the window

    def __init__(self):
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        self.miniWindow = pygame.Surface((
            self.WINDOW_SIZE[0] / src.constants.PX_SCALE_FACTOR,
            self.WINDOW_SIZE[1] / src.constants.PX_SCALE_FACTOR
        ))

        pygame.display.set_caption("BPA Game")

        self.clock = pygame.time.Clock()

        self.closeWindow = False 

        self.inputs = {
            "left": False,
            "right": False,
            "up": False
        }
        self.mousePos = (0, 0)
        self.mousePressed = {
            "left": False,
            "right": False
        }
    
    
    def update_inputs(self):
        self.inputs["up"] = False

        self.mousePos = (
            pygame.mouse.get_pos()[0] // src.constants.PX_SCALE_FACTOR,
            pygame.mouse.get_pos()[1] // src.constants.PX_SCALE_FACTOR,
        )

        self.mousePressed["left"] = pygame.mouse.get_pressed()[0]
        self.mousePressed["right"] = pygame.mouse.get_pressed()[2]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closeWindow = True

            elif event.type == pygame.KEYDOWN:
                if event.key in src.constants.RIGHT_KEYS:
                    self.inputs["right"] = True
                elif event.key in src.constants.LEFT_KEYS:
                    self.inputs["left"] = True
                elif event.key in src.constants.UP_KEYS:
                    self.inputs["up"] = True
            
            elif event.type == pygame.KEYUP:
                if event.key in src.constants.RIGHT_KEYS:
                    self.inputs["right"] = False
                elif event.key in src.constants.LEFT_KEYS:
                    self.inputs["left"] = False


    def flip(self):
        scaledWindow = pygame.transform.scale(self.miniWindow, self.WINDOW_SIZE)
        self.window.blit(scaledWindow, (0, 0))

        pygame.display.flip()

        # UNCOMMENT THIS AFTER TESTING FPS
        # self.clock.tick(src.constants.FPS)

        self.miniWindow.fill((255, 255, 255))