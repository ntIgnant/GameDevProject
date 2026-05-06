import os
import pygame
import Game.settings as settings # Overall game settings (res, fps, ...)
import Game.audio as audio # SFX

# Paths to background and other assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")
BG_PATH = os.path.join(ASSETS_DIR, "BG.png") # Different background image for the menu_settings
BACK_BTN_PATH = os.path.join(ASSETS_DIR, "Backward_BTN.png")

# Aspect ration and size of the 'back' button
BACK_RECT = pygame.Rect(20, 20, 80, 80) # Button placement on screen (now top left)
background_img = None
back_btn_img = None

# Loads the assets used for the menu, and aplies scalation for some (mainly for the buttons)
def load_settings_assets():
    global background_img, back_btn_img

    background_img = pygame.image.load(BG_PATH).convert()
    background_img = pygame.transform.smoothscale(background_img, (settings.WIDTH, settings.HEIGHT))

    back_btn_img = pygame.image.load(BACK_BTN_PATH).convert_alpha()
    back_btn_img = pygame.transform.smoothscale(back_btn_img,(BACK_RECT.width, BACK_RECT.height))

def draw(screen):
    global background_img, back_btn_img

    if background_img is None:
        load_settings_assets()

    screen.blit(background_img, (0, 0))

    if back_btn_img is None:
        load_settings_assets()

    # Title and text settings
    font_title = pygame.font.SysFont("Orbitron", 60, bold=True)
    title1 = font_title.render("CONTROLS", True, (255, 255, 255))
    title2 = font_title.render("RULES", True, (255, 255, 255))
    screen.blit(title1, title1.get_rect(center=(settings.WIDTH // 4, 150)))
    screen.blit(title2, title2.get_rect(center=((settings.WIDTH // 4) * 3 , 150)))
    
    font = pygame.font.SysFont("Orbitron", 38, bold=True)
    
    rows_y = 260
    rows_gap = 40
    
    left_column_x = settings.WIDTH // 4
    right_column_x = (settings.WIDTH // 4) * 3
    
    # List were the strings with the controls/rules text are stored for each column 
    left_lines = ["Movement : WASD", "Shoot : Left Click", "Dash Ability : E", "Frezee Ability : Q"]
    right_lines = ["You are an astronaut trying to escape from the", "spaceship after you were kidnapped by aliens", "You have to go through 3 different rooms", "and beat all aliens to be able to escape"]

    # Display the lines on the left column
    for i, text in enumerate(left_lines):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, surface.get_rect(center = (left_column_x, rows_y + i * rows_gap)))
    
    # List of lines ofsets on the y axis to be able to have custom gaps between some lines
    right_y_gaps = [0, rows_gap,  rows_gap * 3, rows_gap * 4] 
    # Display the lines on the right column    
    for i, text in enumerate(right_lines):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, surface.get_rect(center = (right_column_x, rows_y + right_y_gaps[i])))

    # 'Back' button settings, to go back to main menu
    screen.blit(back_btn_img, BACK_RECT.topleft)
    
def handle_event(event):
    # Key 'Esc' also works to go back 
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return "back"

    if event.type == pygame.MOUSEBUTTONDOWN:
        if BACK_RECT.collidepoint(event.pos):
            audio.play_sound("button_click") # play click sfx when button gets clicked
            return "back"

