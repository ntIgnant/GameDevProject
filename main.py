# Orchestrator (game flow)
import pygame

import Game.settings as settings
import Game.menu as menu
import Game.Level_1.level_1 as level_1

pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Game name")
clock = pygame.time.Clock()

level_1.load_assets()

running = True
main_menu = True

while running:
    dt = clock.tick(settings.FPS) / 1000.0
    keys = pygame.key.get_pressed() # listen to keys to be pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if main_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu.START_RECT.collidepoint(event.pos):
                    main_menu = False
                    level_1.start_level()
        else:
            level_1.handle_level_event(event)

    # draw current state
    if main_menu:
        menu.draw_main_screen(screen)
    else:
        level_1.update_level(dt, keys)
        level_1.draw_level(screen)

    pygame.display.update()

pygame.quit()