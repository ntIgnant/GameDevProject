import pygame
import os
import Game.settings as settings # This is mainly for the resolution (HD, or FHD)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Game_over")
PAUSE_ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "pause_menu")

BG_PATH =  os.path.join(ASSETS_DIR, "BG_game_over.png")
WINDOW_PATH = os.path.join(PAUSE_ASSETS_DIR, "Window.png")
HEADER_PATH = os.path.join(ASSETS_DIR, "you_lost.png")
REPLAY_PATH = os.path.join(ASSETS_DIR, "Replay_BTN.png")
MENU_PATH = os.path.join(PAUSE_ASSETS_DIR, "Menu_BTN.png")

background_raw = None
window_raw = None
header_raw = None
replay_btn_raw = None
menu_btn_raw = None

background_img = None
window_img = None
header_img = None
replay_btn_img = None
menu_btn_img = None

#They start empty, the after rebuild_layout() they will have the current screen size
retry_rect = pygame.Rect(0, 0, 0, 0)
menu_rect = pygame.Rect(0, 0, 0, 0)
window_rect = pygame.Rect(0, 0, 0, 0)
header_rect = pygame.Rect(0, 0, 0, 0)

title_font = None
screen_size = (0, 0)

def load_assets():
    global window_raw, header_raw, replay_btn_raw, menu_btn_raw, background_raw
    
    #Load all images from the folders
    if window_raw is None:
        background_raw = pygame.image.load(BG_PATH).convert()
        window_raw = pygame.image.load(WINDOW_PATH).convert_alpha()
        header_raw = pygame.image.load(HEADER_PATH).convert_alpha()
        replay_btn_raw = pygame.image.load(REPLAY_PATH).convert_alpha()
        menu_btn_raw = pygame.image.load(MENU_PATH).convert_alpha()

    rebuild_layout()


def rebuild_layout():
    global window_img, header_img, replay_btn_img, menu_btn_img, background_img
    global window_rect, header_rect, retry_rect, menu_rect
    global title_font, screen_size

    if window_raw is None:
        return
    
    background_img = pygame.transform.smoothscale(background_raw, (settings.WIDTH, settings.HEIGHT))
    
    scale = min(settings.WIDTH / 1280, settings.HEIGHT / 720)

    #Resizing the window art to fit the current screen
    panel_scale = min(
        (settings.WIDTH * 0.42) / window_raw.get_width(),
        (settings.HEIGHT * 0.76) / window_raw.get_height(),
    )
    panel_scale = max(panel_scale, 0.35)

    panel_width = int(window_raw.get_width() * panel_scale)
    panel_height = int(window_raw.get_height() * panel_scale)
    window_img = pygame.transform.smoothscale(window_raw, (panel_width, panel_height))
    window_rect = window_img.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))

    #Placing the "You Lost" header to fit in the window header area
    header_width = int(window_rect.width * 0.62)
    header_height = int(header_raw.get_height() * (header_width / header_raw.get_width()))
    header_img = pygame.transform.smoothscale(header_raw, (header_width, header_height))
    header_rect = header_img.get_rect(
        center=(window_rect.centerx, window_rect.top + int(window_rect.height * 0.07))
    )
   
    button_size = max(92, int(108 * scale))
    button_gap = max(28, int(34 * scale))
    button_y = window_rect.top + int(window_rect.height * 0.62)
    button_offset = (button_size + button_gap) // 2


    replay_btn_img = pygame.transform.smoothscale(replay_btn_raw, (button_size, button_size))
    menu_btn_img = pygame.transform.smoothscale(menu_btn_raw, (button_size, button_size))
    retry_rect = replay_btn_img.get_rect(center=(window_rect.centerx - button_offset, button_y))
    menu_rect = menu_btn_img.get_rect(center=(window_rect.centerx + button_offset, button_y))

    title_font = pygame.font.SysFont("Orbitron", max(20, int(26 * scale)), bold=True)
    screen_size = (settings.WIDTH, settings.HEIGHT)


def ensure_ready():
    #If the asstest were not loaded, load them
    if window_raw is None:
        load_assets()

    #If the resultion changed, rebuild all assets
    if screen_size != (settings.WIDTH, settings.HEIGHT):
        rebuild_layout()


# This function handles the POST actions of the buttons
# For now, retry and menu button logic
def overlay_action(pos):
    ensure_ready()
    if retry_rect.collidepoint(pos):
        return "retry"
    if menu_rect.collidepoint(pos):
        return "menu"
    return None


def draw_overlay(screen):
    ensure_ready()

    screen.blit(background_img, (0,0))

    screen.blit(make_layer(window_rect.size, (0, 0, 0, 70)), window_rect.move(0, 10).topleft)

    #Draw the game over window and its header "You Lost"
    screen.blit(window_img, window_rect.topleft)
    screen.blit(header_img, header_rect.topleft)

    subtitle = title_font.render("Choose an action", True, (228, 240, 255))
    subtitle_rect = subtitle.get_rect(
        center=(window_rect.centerx, window_rect.top + int(window_rect.height * 0.30))
    )
    screen.blit(subtitle, subtitle_rect)

    # Buttons for Retry and Menu
    mouse_pos = pygame.mouse.get_pos()
    draw_button(screen, replay_btn_img , retry_rect, "Retry", mouse_pos, primary=True)
    draw_button(screen, menu_btn_img ,menu_rect, "Main Menu", mouse_pos)


# Function for the styles of the buttons and text (black and white for now)
def draw_button(screen, image, rect, label, mouse_pos, primary=False):
    
    #If the mouse is over a button, draw a glow effect behind it
    glow_color = (130, 232, 255, 75) if primary else (106, 219, 255, 55)
    if rect.collidepoint(mouse_pos):
        glow_rect = rect.inflate(18, 18)
        glow = make_layer(glow_rect.size, (0, 0, 0, 0))
        pygame.draw.ellipse(glow, glow_color, glow.get_rect())
        screen.blit(glow, glow_rect.topleft)

    #Draw the button image and its text label
    screen.blit(image, rect.topleft)
    label_color = (255, 255, 255) if primary else (241, 246, 255)
    label_surface = title_font.render(label, True, label_color)
    label_rect = label_surface.get_rect(center=(rect.centerx, rect.bottom + 28))
    screen.blit(label_surface, label_rect)


def make_layer(size, color):
    #small helper for creating transparent overlay surfaces 
    layer = pygame.Surface(size, pygame.SRCALPHA)
    layer.fill(color)
    return layer
