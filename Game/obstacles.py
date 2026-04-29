import random
import pygame
import Game.settings as settings

class Obstacles:
    def __init__(self):
        self.height = 59
        self.width = 98
        self.color = (101,67,33)
        self.coordinates = []
        self.corner_blockers = []
        self.image = pygame.image.load("Assets/Background/Obstacles/box_obstacle.png").convert_alpha()
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

    @property
    def collision_rects(self):
        return self.coordinates + self.corner_blockers

    def set_corner_blockers(self, rects):
        self.corner_blockers = [pygame.Rect(rect) for rect in rects]

    def spawn(self, amount=6, area_rect=None):
        self.coordinates = []
        if area_rect is None:
            area_rect = pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT)

        while len(self.coordinates) < amount:
            max_x = area_rect.right - self.image_width
            max_y = area_rect.bottom - self.image_height

            if max_x <= area_rect.left or max_y <= area_rect.top:
                break

            x = random.randrange(area_rect.left, max_x + 1)
            y = random.randrange(area_rect.top, max_y + 1)
            new_rect = pygame.Rect(x, y, self.image_width, self.image_height)
            overlap = False
            #not to spawn the obstacles on top of the player
            spawn = [pygame.Rect(settings.WIDTH // 2.3, settings.HEIGHT // 2.3, 150, 150)]
            # Reject positions that overlap restricted corner blockers or existing obstacles.
            for rect in self.collision_rects + spawn:
                if new_rect.colliderect(rect):
                    overlap = True
                    break
            spawn = []
            if not overlap:
                self.coordinates.append(new_rect)

    def draw(self, screen, camera):
        for rect in self.coordinates:
            
            obstacle_camera_frame = camera.apply(rect)

            image_scaled = pygame.transform.scale(self.image, (self.width, self.height))

            # drawing the obstacle
            screen.blit(image_scaled, obstacle_camera_frame)






