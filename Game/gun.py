import pygame

class GunProjectiles:
    def __innit__(self):
        self.size = 20
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.speed = 500
        self.color = (255, 0, 0)

    def update(self):
        pass

    def draw(self,screen):
        pygame.draw.rect(screen, self.color, self.rect)