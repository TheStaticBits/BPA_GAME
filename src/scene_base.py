import pygame
import logging
import os

import src.constants as constants

class SceneBase:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")

        # If the folder that the event log is in does not exist, create it
        if not os.path.exists(constants.EVENT_LOG_PATH.split("/")[0]):
            os.makedirs(constants.EVENT_LOG_PATH.split("/")[0])

        handler = logging.FileHandler(constants.EVENT_LOG_PATH)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        self.logger.info("Initiating Scene...")


    def update(self):
        self.logger.info("Updating Scene...")


    def render(self):
        self.logger.info("Rendering Scene...")