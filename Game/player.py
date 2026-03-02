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
        self.dash_distance = 140
        self.dash_cooldown = 5.0
        self.dash_cooldown_remaining = 0.0
        self.dash_requested = False
        self.last_move_dir = pygame.Vector2(1, 0)

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.dash_requested = True

    def _apply_dash(self, dash_dir):
        if self.dash_cooldown_remaining > 0:
            return

        self.rect.x += int(dash_dir.x * self.dash_distance)
        self.rect.y += int(dash_dir.y * self.dash_distance)
        if dash_dir.x != 0:
            self.facing_right = dash_dir.x > 0
        self.dash_cooldown_remaining = self.dash_cooldown

    def update(self, dt, keys):
        if self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining = max(0, self.dash_cooldown_remaining - dt)

        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]

        moving = (dx != 0 or dy != 0)
# normalising so diagonal movement isn't faster
        if moving:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.last_move_dir.update(dx, dy)

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

        if self.dash_requested:
            if moving:
                dash_dir = pygame.Vector2(dx, dy)
            else:
                dash_dir = self.last_move_dir.copy()
                if dash_dir.length_squared() == 0:
                    dash_dir = pygame.Vector2(1 if self.facing_right else -1, 0)
            self._apply_dash(dash_dir)
            self.dash_requested = False

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        frame = self.frames[self.frame_index]
# flip when moving left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        screen.blit(frame, frame.get_rect(center=self.rect.center))
