import pygame
import logging

class SceneBase:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

        handler = logging.FileHandler("events.log")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        self.logger.info("Initiating Scene...")


    def update(self):
        self.logger.info("Updating Scene...")


    def render(self):
        self.logger.info("Rendering Scene...")