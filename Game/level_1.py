import os
import pygame
from .settings import WIDTH, HEIGHT

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets") # BASE_DIR is the root of the prj

background = pygame.image.load(
    os.path.join(ASSETS_DIR, "Background", "demo1.png")
)

background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def draw_level(screen):
    screen.blit(background, (0,0))