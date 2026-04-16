import pygame
import os
import Game.settings as settings

# creating a camera that zooms in on the player and follows them (which will be in the center)

class Camera():
    def __init__(self):
        self.offset = pygame.math.Vector2()
        self.width = settings.WIDTH
        self.height = settings.HEIGHT
        self.zoom = 2.2

    def update(self, player):
        self.width = settings.WIDTH
        self.height = settings.HEIGHT

        # zooming in means that the part of the part of world that is visible becomes smaller
        camera_width = self.width // self.zoom
        camera_height = self.height // self.zoom

        # the player has to be in the center
        self.offset.x = player.rect.centerx - camera_width // 2
        self.offset.y = player.rect.centery - camera_height // 2

    def apply(self, rect):
        # making the world seem bigger (applying the zoom effect)
        return pygame.Rect((rect.x - self.offset.x) * self.zoom, (rect.y - self.offset.y) * self.zoom, rect.width * self.zoom, rect.height * self.zoom)
