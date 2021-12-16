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
        )) # Miniwindow is the window divided by the pixel scale factor

        pygame.display.set_caption("There Is Nothing")

        self.clock = pygame.time.Clock()

        self.closeWindow = False 

        self.inputs = {
            "left": False,
            "right": False,
            "up": False,
            "space": False,
            "esc": False,
            "enter": False
        }
        self.mousePos = (0, 0)
        self.mousePressed = {
            "left": False,
            "center": False,
            "right": False
        }

        self.inputButtons = {
            "left": constants.LEFT_KEYS,
            "right": constants.RIGHT_KEYS,
            "up": constants.UP_KEYS,
            "space": [pygame.K_SPACE],
            "esc": [pygame.K_ESCAPE],
            "enter": [pygame.K_RETURN]
        }
    
    
    def update_inputs(self):
        # Resets inputs that are one time, iterates through Pygame events and takes note of inputs.

        # Resetting one-time inputs
        self.inputs["up"] = False
        self.inputs["space"] = False
        self.inputs["esc"] = False
        self.inputs["enter"] = False

        # Getting mouse positions and buttons pressed
        self.mousePos = (
            pygame.mouse.get_pos()[0] // constants.PX_SCALE_FACTOR,
            pygame.mouse.get_pos()[1] // constants.PX_SCALE_FACTOR,
        )

        self.mousePressed["left"], self.mousePressed["center"], self.mousePressed["right"] = pygame.mouse.get_pressed()
        
        # Iterating through all events/inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closeWindow = True

            elif event.type == pygame.KEYDOWN:
                # If there was a key pressed down, sets the corresponding key to true
                for key in self.inputButtons:
                    if event.key in self.inputButtons[key]:
                        self.inputs[key] = True
            
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

        self.miniWindow.fill(constants.BLACK)