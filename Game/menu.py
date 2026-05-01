import os
import pygame
import Game.settings as settings # Overall game settings (res, fps, ...)
import Game.audio as audio


# MENU ASSETS DIRECTORY
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")

BG_PATH = os.path.join(ASSETS_DIR, "BG_ver02.png") # updated to alien version
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
    background_img = pygame.transform.smoothscale(background_img, (settings.WIDTH, settings.HEIGHT))

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

background_color = (252, 252, 255) # Default background color (as fallbac in case background image does't load properly)

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
    font_title = pygame.font.SysFont("Orbitron-Regular.ttf", font_size, bold=True)
    title_text = font_title.render("Alien Outbreak", True, (255, 255, 255))
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
        audio.play_sound("button_click")
        return "continue" # This label may change depending on the list LEVELS_COMPLETED in settings.py
    if NEW_GAME_RECT.collidepoint(pos):
        audio.play_sound("button_click")
        return "new_game"
    if SETTINGS_RECT.collidepoint(pos):
        audio.play_sound("button_click")
        return "settings"
    if EXIT_RECT.collidepoint(pos):
        audio.play_sound("button_click")
        return "exit"

    return None

# Function for the 'switch resolution'. to re-scale the menu layout
def rebuild_layout():
    global TITLE_RECT, START_RECT, NEW_GAME_RECT, SETTINGS_RECT, EXIT_RECT
    global background_img, start_btn_img, new_game_btn_img, settings_btn_img, exit_btn_img

    # Scale to HD. Here the Height is not fowrced because there was a bug with it, but this is HD re-scale
    scale = settings.WIDTH / 1280

    # Re-scale Title rectangle
    title_w = int(500 * scale)
    title_h = int(100 * scale)
    TITLE_RECT = pygame.Rect(0, 0, title_w, title_h)
    TITLE_RECT.center = (settings.WIDTH // 2, int(settings.HEIGHT * 0.25))

    # Buttons re-scale
    btn_w = int(220 * scale)
    btn_h = int(60 * scale)
    START_RECT = pygame.Rect(0, 0, btn_w, btn_h)
    NEW_GAME_RECT = pygame.Rect(0, 0, btn_w, btn_h)
    SETTINGS_RECT = pygame.Rect(0, 0, btn_w, btn_h)
    EXIT_RECT = pygame.Rect(0, 0, btn_w, btn_h)

    gap = int(18 * scale)
    cx = settings.WIDTH // 2
    base_y = int(settings.HEIGHT * 0.48)

    START_RECT.center = (cx, base_y)
    NEW_GAME_RECT.center = (cx, base_y + (btn_h + gap))
    SETTINGS_RECT.center = (cx, base_y + 2 * (btn_h + gap))
    EXIT_RECT.center = (cx, base_y + 3 * (btn_h + gap))

    # Force image reload to apply re-scaling and avoid wierd sizes
    background_img = None
    start_btn_img = None
    new_game_btn_img = None
    settings_btn_img = None
    exit_btn_img = None
