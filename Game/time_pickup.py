import os
import pygame

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TIME_PICKUP_IMAGE_PATH = os.path.join(BASE_DIR, "Assets", "pickups", "time_bonus.png")


class TimePickup:
    def __init__(self, center, bonus_seconds=15):
        self.size = 28
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = center
        self.bonus_seconds = bonus_seconds
        self.collected = False
        self.image = pygame.image.load(TIME_PICKUP_IMAGE_PATH).convert_alpha()
        self.font = pygame.font.Font(None, 20)

    def update(self, dt):
        return

    def try_collect(self, player_rect, timer):
        if self.collected:
            return False

        if player_rect.colliderect(self.rect):
            timer.add_seconds(self.bonus_seconds)
            self.collected = True
            return True

        return False

    def draw(self, screen, camera):
        if self.collected:
            return

        camera_rect = camera.apply(self.rect)
        pickup_image = pygame.transform.smoothscale(
            self.image,
            (max(1, camera_rect.width), max(1, camera_rect.height)),
        )
        screen.blit(pickup_image, camera_rect.topleft)

        label = self.font.render(f"+{self.bonus_seconds}", True, (235, 248, 255))
        label_rect = label.get_rect(midtop=(camera_rect.centerx, camera_rect.bottom + 4))
        screen.blit(label, label_rect)
