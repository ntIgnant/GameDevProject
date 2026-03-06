import pygame

class GunProjectile:
    def __init__(self, x, y, direction):
        self.size = 10
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.direction = direction
        self.speed = 500
        self.color = (255, 0, 0)

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

    def draw(self, screen, camera):
        rect = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, rect)