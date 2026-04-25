# Orchestrator (game flow)
import pygame

import Game.settings as settings # Config file of the game (e.g resolution, fps, etc)
import Game.menu as menu # Menu logic
import Game.menu_settings as menu_settings # settings menu logic
import Game.Level_1.level_1 as level_1 # Level 1 logic
import Game.Level_2.level_2 as level_2 # Level 2 logic
import Game.pause_menu as pause_menu
import Game.game_over as game_over
import Game.audio as audio

pygame.init()
audio.init_audio()
audio.load_game_sfx()

screen = pygame.display.set_mode(settings.CURRENT_SCREEN_SIZE)

# Functions to force resolution scale, to avoid bugs of resolution
menu.rebuild_layout()
menu.load_menu_assets()
menu_settings.rebuild_layout()
pause_menu.load_assets()
game_over.rebuild_layout()

pygame.display.set_caption("Game name")
clock = pygame.time.Clock()

level_1.load_assets()
level_2.load_assets()

running = True # boolean for the general game loop
state = "menu" # this will vary depending on the state of the game [menu, menu_settings, level, etc]
current_level = level_1

# Function to start level depending on the 'current last' level
# It initializes with level 1
def start_level(level_module):
    global current_level, state

    current_level = level_module
    current_level.start_level()
    state = "level"

# Global loop of the Game
while running:
    dt = clock.tick(settings.FPS) / 1000.0
    keys = pygame.key.get_pressed() # listen to keys to be pressed
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Handle options of the main menu
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = menu.menu_options_handler(event.pos)

                # Case when the 'new game' button is pressed | start from level 1
                if action == "new_game":
                    settings.LEVELS_COMPLETED.clear() # Clear all the completed levels to start a new game
                    start_level(level_1)
                
                # Case when the 'continue / start' button is pressed | start the game from the last level that was completed
                elif action == "continue":
                    if not settings.LEVELS_COMPLETED:
                        next_level = 1
                    else:
                        next_level = max(settings.LEVELS_COMPLETED) + 1 # get the last completed level + 1 = current level to be played

                    # Evalueate level execution based on next_level value
                    if next_level == 1:
                        start_level(level_1)
                    elif next_level == 2:
                        start_level(level_2)
                    else:
                        start_level(level_1)

                elif action == "settings":
                    state = "menu_settings" # change state to menu_settings to display the settings menu

                elif action == "exit":
                    running = False # Exit the while loop and terminate the game

        # Case where the button 'settings' is pressed -> jump to settings pannel to let the user modify values
        elif state == "menu_settings":
            action = menu_settings.handle_event(event)
            # Case of 'back' button inside settings menu
            if action == "back":
                state = "menu"
            
            # Case of 'switch resolution' in settings menu
            elif action == "switch_resolution":
                screen = pygame.display.set_mode(settings.CURRENT_SCREEN_SIZE)

                # In the change of resolution, it can get wierd because the assets have fixed resolutions and sizes
                # If the 'switch resolution' settings is gonna be applied, we need to recreate the assets in the new size (HD and FHD for each used asset)
                menu.rebuild_layout()
                menu.load_menu_assets()
                menu_settings.rebuild_layout()
                pause_menu.rebuild_layout()
                game_over.rebuild_layout()
                level_1.rebuild_layout()
                level_2.rebuild_layout()
        
        # Case where 'game_over' flag is returned
        # This triggers the game over screen to the user
        # TODO:  game over screen style needs to be improved Game/game_over.py
        elif state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = game_over.overlay_action(event.pos)
                if action == "retry":
                    start_level(current_level)
                elif action == "menu":
                    state = "menu"
            

    level_action = None
    if state == "level":
        level_action = current_level.update_level(dt, keys, events)
        if level_action == "menu":
            state = "menu"
        elif level_action == "game_over":
            state = "game_over"

        # Action to 'jump to a next level'
        # TODO: add level_3 statement
        elif level_action == "level_complete":
            if current_level is level_1:
                if 1 not in settings.LEVELS_COMPLETED:
                    settings.LEVELS_COMPLETED.append(1)
                start_level(level_2)

    # draw current state
    if state == "menu":
        menu.draw_main_screen(screen)
    elif state == "menu_settings":
        # screen.fill((10, 15, 30)) # placeholder for now | here should be the draw of the settings menu
        menu_settings.draw(screen)
    elif state == "level":
        current_level.draw_level(screen)
    elif state == "game_over":
        game_over.draw_overlay(screen)

    pygame.display.update()

audio.stop_all_sfx()
pygame.quit()
