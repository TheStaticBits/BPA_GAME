import pygame
import src.constants as constants

"""
This class creates, manages, and updates the Pygame Window.
It also manages the inputs from the user
"""
class Window:
    WINDOW_SIZE = (
        constants.PX_SCALE_FACTOR * constants.SCREEN_SIZE[0],
        constants.PX_SCALE_FACTOR * constants.SCREEN_SIZE[1]
    ) # This is the size of the window

    def __init__(self):
        # Creates the window, the miniwindow, sets up other Pygame things, and inputs.

        self.window = pygame.display.set_mode(self.WINDOW_SIZE, pygame.DOUBLEBUF)
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
            "up": False,
            "space": False,
            "esc": False
        }
        self.mousePos = (0, 0)
        self.mousePressed = {
            "left": False,
            "center": False,
            "right": False
        }
    
    
    def update_inputs(self):
        # Resets inputs that are one time, iterates through Pygame events and takes note of inputs.

        # Resetting one-time inputs
        self.inputs["up"] = False
        self.inputs["space"] = False
        self.inputs["esc"] = False

        # Getting mouse positions and buttons pressed
        self.mousePos = (
            pygame.mouse.get_pos()[0] // constants.PX_SCALE_FACTOR,
            pygame.mouse.get_pos()[1] // constants.PX_SCALE_FACTOR,
        )

        self.mousePressed["left"] = pygame.mouse.get_pressed()[0]
        self.mousePressed["center"] = pygame.mouse.get_pressed()[1]
        self.mousePressed["right"] = pygame.mouse.get_pressed()[2]
        
        # Iterating through all events/inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closeWindow = True

            elif event.type == pygame.KEYDOWN:
                # If there was a key pressed down, sets the corresponding key to true
                if event.key in constants.RIGHT_KEYS:
                    self.inputs["right"] = True
                elif event.key in constants.LEFT_KEYS:
                    self.inputs["left"] = True
                elif event.key in constants.UP_KEYS:
                    self.inputs["up"] = True
                elif event.key == pygame.K_SPACE:
                    self.inputs["space"] = True
                elif event.key == pygame.K_ESCAPE:
                    self.inputs["esc"] = True
            
            elif event.type == pygame.KEYUP:
                # If there was a key let go, sets the corresponding non-one-time keys to false

                if event.key in constants.RIGHT_KEYS:
                    self.inputs["right"] = False
                elif event.key in constants.LEFT_KEYS:
                    self.inputs["left"] = False


    def flip(self):
        # Scales up the miniwindow and updates the screen with it, stablizing frame rate and also clearing the miniwindow afterwards.

        scaledWindow = pygame.transform.scale(self.miniWindow, self.WINDOW_SIZE)
        self.window.blit(scaledWindow, (0, 0))

        pygame.display.flip()

        if constants.CAP_FPS:
            self.clock.tick(constants.FPS) # Manages the framerate

        self.miniWindow.fill((0, 0, 0))