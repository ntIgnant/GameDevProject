import pygame
import random

class Upgrades:
    def __init__ (self, x, y):
        self.height = 40
        self.width = 35
        self.color = (101,67,33)
        self.image = pygame.image.load("Assets/Extras/posion.png").convert_alpha()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.rect = pygame.Rect(x, y, self.image_width, self.image_height)


    def draw(self, screen, camera):
        rect = camera.apply(self.rect)

        image_scaled = pygame.transform.scale(self.image, (self.width, self.height))

        screen.blit(image_scaled, rect)

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

