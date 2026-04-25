import pygame
import random

class Upgrades:
    def __init__ (self, x, y):
        self.size = 20
        self.color = (101,67,33)
        self.rect = pygame.Rect(x, y, self.size, self.size)


    def draw(self, screen, camera):
        rect = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, rect)

    # Generate random number witch decides what upgrade the player is going to get
    def random_upgrade(self, player):
        number = random.randint(1, 3)
        center = player.rect.center

        if number == 1:
            player.size -= 20
        elif number == 2:   
            player.max_health += 20
            player.health += 20
        elif number == 3:
            player.speed += 200

        player.rect.size = (player.size, player.size)
        player.rect.center = center

