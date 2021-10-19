import pygame

# So, this could be used for error handling, which is something that all scenes have the need for.

class SceneBase:
    def __init__(self):
        print("Initializing Scene...")


    def update(self):
        print("Updating Scene...")


    def render(self):
        print("Rendering Scene...")