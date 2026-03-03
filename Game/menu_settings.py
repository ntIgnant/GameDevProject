import os
import pygame
from .settings import WIDTH, HEIGHT
from . import menu  # this import is to reuse functions created in menu.py file

# Paths to background and other assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")
BACK_BTN_PATH = os.path.join(ASSETS_DIR, "Back_BTN.png")

BACK_RECT = pygame.Rect(0, 0, 220, 60)
BACK_RECT.center = (WIDTH // 2, int(HEIGHT * 0.8))

back_btn_img = None

def load_settings_assets():
    global back_btn_img

    back_btn_img = pygame.image.load(BACK_BTN_PATH).convert_alpha()
    back_btn_img = pygame.transform.smoothscale(
        back_btn_img,
        (BACK_RECT.width, BACK_RECT.height)
    )


def draw(screen):
    global back_btn_img

    # Background img (same as menu)
    if menu.background_img is None:
        menu.load_menu_assets()

    screen.blit(menu.background_img, (0, 0))

    if back_btn_img is None:
        load_settings_assets()

    # Title and text settings
    font_title = pygame.font.SysFont("Orbitron", 60, bold=True)
    title = font_title.render("SETTINGS", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

    # 'Back' button settings, to go back to main menu
    screen.blit(back_btn_img, BACK_RECT.topleft)

    mouse_pos = pygame.mouse.get_pos()

    if BACK_RECT.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), BACK_RECT, 2, border_radius=10)


def handle_event(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return "back"

    if event.type == pygame.MOUSEBUTTONDOWN:
        if BACK_RECT.collidepoint(event.pos):
            return "back"

    return None