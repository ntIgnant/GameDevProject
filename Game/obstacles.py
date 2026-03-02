import random
import pygame
from .settings import WIDTH, HEIGHT

class Obstacles:
    def __init__(self):
        self.size = 40
        self.color = (101,67,33)
        self.coordinates = []
        self.image = pygame.image.load("Assets/Background/Obstacles/disc_obstacle.png")
        self.image = pygame.transform.scale(self.image,(self.size, self.size))

    def spawn(self, amount=6):
        while len(self.coordinates) < amount:
            x = random.randrange(250, WIDTH - self.size - 240)
            y = random.randrange(310, HEIGHT - self.size - 150)
            new_rect = pygame.Rect(x, y, self.size, self.size)
            overlap = False
            #check for overlapping with other obstacles
            for rect in self.coordinates:
                if new_rect.colliderect(rect):
                    overlap = True
                    break
            if not overlap:
                self.coordinates.append(new_rect)

    def draw(self, screen):
        for rect in self.coordinates:
            screen.blit(self.image,rect)





