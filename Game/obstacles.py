import random
import pygame
from .settings import WIDTH, HEIGHT

class Obstacles:
    def __init__(self):
        self.size = 40
        self.color = (101,67,33)
        self.coordinates = []
        self.corner_blockers = []
        self.image = pygame.image.load("Assets/Background/Obstacles/disc_obstacle.png").convert_alpha()
        self.image_cropped = pygame.transform.scale(self.image,(80,80))

    @property
    def collision_rects(self):
        return self.coordinates + self.corner_blockers

    def set_corner_blockers(self, rects):
        self.corner_blockers = [pygame.Rect(rect) for rect in rects]

    def spawn(self, amount=6, area_rect=None):
        self.coordinates = []
        if area_rect is None:
            area_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

        while len(self.coordinates) < amount:
            max_x = area_rect.right - self.size
            max_y = area_rect.bottom - self.size

            if max_x <= area_rect.left or max_y <= area_rect.top:
                break

            x = random.randrange(area_rect.left, max_x + 1)
            y = random.randrange(area_rect.top, max_y + 1)
            new_rect = pygame.Rect(x, y, self.size, self.size)
            overlap = False
            #check for overlapping with other obstacles
            for rect in self.coordinates:
                if new_rect.colliderect(rect):
                    overlap = True
                    break
            if not overlap:
                self.coordinates.append(new_rect)

    def draw(self, screen, camera):
        for rect in self.coordinates:
            
            obstacle_camera_frame = camera.apply(rect)

            # drawing the obstacle
            screen.blit(self.image_cropped, obstacle_camera_frame)






