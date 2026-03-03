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
        #health(we can connect it to damage later)
        self.max_health = 100
        self.health = 100
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

        ui = pygame.image.load(
            os.path.join(ASSETS_DIR, "Characters", "Player", "Health_Sheet.png")
        ).convert_alpha()

        ui_w, ui_h = ui.get_size()

        HEART_RECT = pygame.Rect(0, 132, 40, 34)
        BG_RECT    = pygame.Rect(31, 60, 92, 13)
        FILL_RECT  = pygame.Rect(31, 100, 92, 13)

        HEART_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        BG_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        FILL_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))

        self.heart_img = ui.subsurface(HEART_RECT).copy()
        self.bar_bg = ui.subsurface(BG_RECT).copy()
        self.bar_fill = ui.subsurface(FILL_RECT).copy()

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

    def update(self, dt, keys, obstacles):
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

           #moving left and right logic
            self.rect.x += int(dx * self.speed * dt)
            for obstacle in obstacles.coordinates:
                if self.rect.colliderect(obstacle):
                    if dx > 0:
                        self.rect.right = obstacle.left #player moving right
                    elif dx < 0:
                        self.rect.left = obstacle.right #player moving left

           #moving up and down logic
            self.rect.y += int(dy * self.speed * dt)
            for obstacle in obstacles.coordinates:
                if self.rect.colliderect(obstacle):
                    if dy > 0:
                        self.rect.bottom = obstacle.top #moving down
                    if dy < 0:
                        self.rect.top = obstacle.bottom #moving up

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
        # TEMP test: health goes down automatically
        self.health = max(0, self.health - 10 * dt)


    def draw_health_ui(self, screen):
        ratio = max(0, min(1, self.health / self.max_health))

        sprite_h = 160
        y = self.rect.centery - sprite_h // 2 - 25

        bar_w = self.bar_bg.get_width()
        bar_x = self.rect.centerx - bar_w // 2

        # bar background
        screen.blit(self.bar_bg, (bar_x, y))

        # bar fill
        max_fill_width = self.bar_bg.get_width()
        fill_w = int(max_fill_width * ratio)
        
        if fill_w > 0:
            fill_part = self.bar_fill.subsurface((0, 0, fill_w, self.bar_fill.get_height()))
            screen.blit(fill_part, (bar_x, y))

        
        heart_x = bar_x - self.heart_img.get_width() // 3 - 10
        heart_y = y - self.heart_img.get_height() // 2 + 5
        screen.blit(self.heart_img, (heart_x, heart_y))

        


    def draw(self, screen):
        frame = self.frames[self.frame_index]
# flip when moving left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        screen.blit(frame, frame.get_rect(center=self.rect.center))
        self.draw_health_ui(screen)
