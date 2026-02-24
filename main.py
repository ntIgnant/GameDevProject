# Orchestrator (game flow)
import pygame

from Game.settings import WIDTH, HEIGHT, FPS
from Game.menu import draw_main_screen, START_RECT
from Game.level_1 import draw_level

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game name")
clock = pygame.time.Clock()

running = True
main_menu = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if main_menu and START_RECT.collidepoint(event.pos):
                main_menu = False

    # draw current state
    if main_menu:
        draw_main_screen(screen)
    else:
        draw_level(screen)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()