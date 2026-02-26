import os
import math
import pygame
from .settings import WIDTH, HEIGHT

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

class Player:
    def __init__(self):
        self.size = 40
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, self.size, self.size)
        self.speed = 300

        # loading walk animation (can be moved elsewhere)
        sheet = pygame.image.load(
            os.path.join(ASSETS_DIR, "Characters", "Player", "player_walk.png")
        ).convert_alpha()

        self.frames = []
        for x in range(0, sheet.get_width(), 32):
            frame = sheet.subsurface((x, 0, 32, 32))
            frame = pygame.transform.scale(frame, (160, 160))#we can adjust the scale if needed
            self.frames.append(frame)

        self.frame_index = 0
        self.timer = 0
        self.facing_right = True

    def handle_event(self, event):
        pass

    def update(self, dt, keys):
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]

        moving = (dx != 0 or dy != 0)
# normalising so diagonal movement isn't faster
        if moving:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            self.rect.x += int(dx * self.speed * dt)
            self.rect.y += int(dy * self.speed * dt)

            if dx != 0:
                self.facing_right = dx > 0

            self.timer += dt
            if self.timer > 0.1:
                self.timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0
            self.timer = 0

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        frame = self.frames[self.frame_index]
# flip when moving left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        screen.blit(frame, frame.get_rect(center=self.rect.center))