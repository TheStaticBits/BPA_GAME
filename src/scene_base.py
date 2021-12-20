import pygame
import logging
import os

import src.constants as constants

"""
All scenes inherit from this class
It creates the logger for the given class and logs the events that occur
"""
class SceneBase:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG) # Sets the level to debug so all logs will show

        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")

        # If the folder that the event.log is in does not exist, create it
        if not os.path.exists(constants.EVENT_LOG_PATH.split("/")[0]):
            os.makedirs(constants.EVENT_LOG_PATH.split("/")[0])
        
        handler = logging.FileHandler(constants.EVENT_LOG_PATH)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        self.logger.info("Initiating Scene...")


    def update(self): # Called by base classes 
        self.logger.info("Updating Scene...")


    def render(self): # Called by base classes 
        self.logger.info("Rendering Scene...")