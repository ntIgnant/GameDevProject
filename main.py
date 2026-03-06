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

# Global loop of the Game
while running:
    dt = clock.tick(settings.FPS) / 1000.0
    keys = pygame.key.get_pressed() # listen to keys to be pressed
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Handle options of the main menu
        if main_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = menu.menu_options_handler(event.pos)

                # Evalueate the action, to check which logic to execute based on the options of the menu
                if action == "new_game":
                    settings.LEVELS_COMPLETED.clear() # Clear all the completed levels to start a new game
                    main_menu = False
                    level_1.start_level()
                
                elif action == "continue":
                    main_menu = False

                    if not settings.LEVELS_COMPLETED:
                        next_level = 1
                    else:
                        next_level = max(settings.LEVELS_COMPLETED) + 1 # get the last completed level + 1 = current level to be played

                    # Evalueate level execution based on next_level value
                    if next_level == 1:
                        level_1.start_level()
                    # TO BE IMPLEMENTED: NEXT LEVELS INITIALIZATION
                    # Start level1 just for now...
                    else:
                        level_1.start_level()

                elif action == "settings":
                    print("Settings Menu should be displayed and allowed for value modification")

                elif action == "exit":
                    running = False # Exit the while loop and terminate the game

    # draw current state
    if main_menu:
        menu.draw_main_screen(screen)
    else:
        level_1.update_level(dt, keys, events)
        level_1.draw_level(screen)

    pygame.display.update()

pygame.quit()