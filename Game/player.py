# General Logic for the player (reusable for all the levels)
import math
import pygame
from .settings import WIDTH, HEIGHT

class Player:
    def __init__(self):
        self.size = 40
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, self.size, self.size)
        self.speed = 300

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.rect.center = event.pos

    # Movement keys (WASD)
    def update(self, dt, keys):
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) # x axis
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) # y axis

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.rect.x += int(dx * self.speed * dt)
            self.rect.y += int(dy * self.speed * dt)

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 200, 0), self.rect)