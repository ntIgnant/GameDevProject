import random
import pygame
from .settings import WIDTH, HEIGHT

class Obstacles:
    def __init__(self):
        self.size = 40
        self.color = (101,67,33)
        self.coordinates = []

    def spawn(self,amount = 10):
        for i in range(amount):
            x = random.randrange(0, WIDTH-self.size)
            y = random.randrange(0, HEIGHT-self.size)

            rect = pygame.Rect(x, y, self.size, self.size)
            self.coordinates.append(rect)

    def draw(self, screen, camera):
        for rect in self.coordinates:
            
            obstacle_camera_frame = camera.apply(rect)

            # drawing the obstacle
            pygame.draw.rect(screen, self.color, obstacle_camera_frame)





