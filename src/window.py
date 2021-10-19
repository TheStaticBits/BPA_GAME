import pygame
import src.constants as constants

class Window:
    WINDOW_SIZE = (
        constants.PX_SCALE_FACTOR * constants.TILE_SIZE[0] * constants.SCREEN_TILE_SIZE[0], 
        constants.PX_SCALE_FACTOR * constants.TILE_SIZE[1] * constants.SCREEN_TILE_SIZE[1]
    ) # This is the size of the window

    def __init__(self):
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        self.miniWindow = pygame.Surface((
            self.WINDOW_SIZE[0] / constants.PX_SCALE_FACTOR,
            self.WINDOW_SIZE[1] / constants.PX_SCALE_FACTOR
        ))

        pygame.display.set_caption("BPA Game")

        self.clock = pygame.time.Clock()

        self.closeWindow = False 

        self.inputs = {
            "left": False,
            "right": False,
            "up": False
        }
    
    
    def update_inputs(self):
        self.inputs["up"] = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closeWindow = True

            elif event.type == pygame.KEYDOWN:
                if event.key in constants.RIGHT_KEYS:
                    self.inputs["right"] = True
                elif event.key in constants.LEFT_KEYS:
                    self.inputs["left"] = True
                elif event.key in constants.UP_KEYS:
                    self.inputs["up"] = True
            
            elif event.type == pygame.KEYUP:
                if event.key in constants.RIGHT_KEYS:
                    self.inputs["right"] = False
                elif event.key in constants.LEFT_KEYS:
                    self.inputs["left"] = False
                

    def flip(self):
        scaledWindow = pygame.transform.scale(self.miniWindow, self.WINDOW_SIZE)
        self.window.blit(scaledWindow, (0, 0))

        pygame.display.flip()

        self.clock.tick(constants.FPS)

        self.miniWindow.fill((0, 0, 0))