import pygame
import os
import math

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Extras")

BULLET_PATH = os.path.join(ASSETS_DIR, "bullet.png")

class GunProjectile:
    bullet_img = None
    
    def __init__(self, x, y, direction):
        #self.size = 10
        if GunProjectile.bullet_img is None:
            bullet_raw= pygame.image.load(BULLET_PATH).convert_alpha()
            GunProjectile.bullet_img = pygame.transform.scale(bullet_raw, (25, 8))
        
        self.pos = pygame.Vector2(x, y)
        self.direction = direction
        self.speed = 500
        #self.color = (255, 0, 0)
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(GunProjectile.bullet_img, angle)
        self.rect = self.image.get_rect(center = (x,y))

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

    def draw(self, screen, camera):
        rect = self.image.get_rect(center = camera.apply(self.rect).center)
        #pygame.draw.rect(screen, self.color, rect)
        screen.blit(self.image, rect)