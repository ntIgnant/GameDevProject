import os
import pygame
from .settings import WIDTH, HEIGHT

# MENU ASSETS DIRECTORY
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")

BG_PATH = os.path.join(ASSETS_DIR, "BG.png")
START_BTN_PATH = os.path.join(ASSETS_DIR, "Start_BTN.png")
NEW_GAME_BTN_PATH = os.path.join(ASSETS_DIR, "New_Game_BTN.png")
SETTINGS_BTN_PATH = os.path.join(ASSETS_DIR, "Settings_BTN.png")
EXIT_BTN_PATH = os.path.join(ASSETS_DIR, "Exit_BTN.png")

background_img = None
start_btn_img = None
exit_btn_img = None
new_game_btn_img = None
settings_btn_img = None

# Load Menu Assets
def load_menu_assets():
    global background_img, start_btn_img, exit_btn_img, new_game_btn_img, settings_btn_img

    # Background Image
    background_img = pygame.image.load(BG_PATH).convert()
    background_img = pygame.transform.smoothscale(background_img, (WIDTH, HEIGHT))

    # 'Start' button Image
    start_btn_img = pygame.image.load(START_BTN_PATH).convert_alpha()
    start_btn_img = pygame.transform.smoothscale(start_btn_img, (START_RECT.width, START_RECT.height))

    # 'New Game' button Image
    new_game_btn_img = pygame.image.load(NEW_GAME_BTN_PATH).convert_alpha()
    new_game_btn_img = pygame.transform.smoothscale(new_game_btn_img, (NEW_GAME_RECT.width, NEW_GAME_RECT.height))

    # 'Settings' button Image
    settings_btn_img = pygame.image.load(SETTINGS_BTN_PATH).convert_alpha()
    settings_btn_img = pygame.transform.smoothscale(settings_btn_img, (SETTINGS_RECT.width, SETTINGS_RECT.height))

    # 'Exit' button Image
    exit_btn_img = pygame.image.load(EXIT_BTN_PATH).convert_alpha()
    exit_btn_img = pygame.transform.smoothscale(exit_btn_img, (EXIT_RECT.width, EXIT_RECT.height))

background_color = (252, 252, 255)

# Definition of rectanles (buttons and titles)
TITLE_RECT = pygame.Rect(0, 0, 500, 100)
TITLE_RECT.center = (WIDTH // 2, HEIGHT // 4)

START_RECT = pygame.Rect(0, 0, 200, 50)
START_RECT.center = (WIDTH // 2, HEIGHT // 2 - 40)

NEW_GAME_RECT = pygame.Rect(0, 0, 200, 50)
NEW_GAME_RECT.center = (WIDTH // 2, HEIGHT // 2 + 20)

SETTINGS_RECT = pygame.Rect(0, 0, 200, 50)
SETTINGS_RECT.center = (WIDTH // 2, HEIGHT // 2 + 80)

EXIT_RECT = pygame.Rect(0, 0, 200, 50)
EXIT_RECT.center = (WIDTH // 2, HEIGHT // 2 + 140)


def draw_main_screen(screen):
    if background_img is None:
        load_menu_assets()

    screen.blit(background_img, (0, 0))

    # Config for the Title and Text (for now)
    panel = pygame.Surface((TITLE_RECT.width, TITLE_RECT.height), pygame.SRCALPHA)
    panel.fill((20, 40, 90, 200))  # Dark blue with transparency
    screen.blit(panel, TITLE_RECT.topleft)

    # Border style
    pygame.draw.rect(screen, (80, 180, 255), TITLE_RECT, 3, border_radius=20)

    # Title text and style
    font_size = int(TITLE_RECT.height * 0.6)
    font_title = pygame.font.SysFont("Orbitron", font_size, bold=True)
    title_text = font_title.render("Epic Name...", True, (255, 255, 255))
    screen.blit(title_text, title_text.get_rect(center=TITLE_RECT.center))

    screen.blit(start_btn_img, START_RECT.topleft)
    screen.blit(new_game_btn_img, NEW_GAME_RECT.topleft)
    screen.blit(settings_btn_img, SETTINGS_RECT.topleft)
    screen.blit(exit_btn_img, EXIT_RECT.topleft)

    mouse_pos = pygame.mouse.get_pos() # object for the mouse possition (to keep track of the button click)

    # Style for the buttons based on the mouse pointer
    if START_RECT.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), START_RECT, 2, border_radius=10)
    if NEW_GAME_RECT.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), NEW_GAME_RECT, 2, border_radius=10)
    if SETTINGS_RECT.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), SETTINGS_RECT, 2, border_radius=10)
    if EXIT_RECT.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), EXIT_RECT, 2, border_radius=10)

def menu_options_handler(pos):
    if START_RECT.collidepoint(pos):
        return "continue" # This label may change depending on the list LEVELS_COMPLETED in settings.py
    if NEW_GAME_RECT.collidepoint(pos):
        return "new_game"
    if SETTINGS_RECT.collidepoint(pos):
        return "settings"
    if EXIT_RECT.collidepoint(pos):
        return "exit"

    return None