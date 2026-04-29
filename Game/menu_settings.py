import os
import pygame
import Game.settings as settings # Overall game settings (res, fps, ...)
import Game.audio as audio # SFX
from . import menu  # this import is to reuse functions created in menu.py file

# Paths to background and other assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")
BACK_BTN_PATH = os.path.join(ASSETS_DIR, "Backward_BTN.png")

# Aspect ration and size of the 'back' button
BACK_RECT = pygame.Rect(20, 20, 80, 80) # Button placement on screen (now top left)
back_btn_img = None

# Rectangles for the reolution settings
RES_Y = 360
RES_LABEL_POS = (0, 0)
RES_VALUE_RECT = pygame.Rect(0, 0, 140, 60)
RES_LEFT_RECT = pygame.Rect(0, 0, 60, 60)
RES_RIGHT_RECT = pygame.Rect(0, 0, 60, 60)

def load_settings_assets():
    global back_btn_img

    back_btn_img = pygame.image.load(BACK_BTN_PATH).convert_alpha()
    back_btn_img = pygame.transform.smoothscale(back_btn_img,(BACK_RECT.width, BACK_RECT.height))


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
    screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, 150)))

    # 'Back' button settings, to go back to main menu
    screen.blit(back_btn_img, BACK_RECT.topleft)

    # Resolution settings panel
    font = pygame.font.SysFont("Orbitron", 28, bold=True)

    # Label
    label = font.render("RESOLUTION", True, (255, 255, 255))
    screen.blit(label, label.get_rect(midleft=RES_LABEL_POS))

    mouse_pos = pygame.mouse.get_pos()

    # Left arrow button
    hovered = RES_LEFT_RECT.collidepoint(mouse_pos)
    fill = (30, 50, 90) if not hovered else (45, 75, 130)
    pygame.draw.rect(screen, fill, RES_LEFT_RECT, border_radius=10)
    pygame.draw.rect(screen, (80, 180, 255), RES_LEFT_RECT, 2, border_radius=10)
    pygame.draw.polygon(screen, (255, 255, 255), [
        (RES_LEFT_RECT.centerx + 8, RES_LEFT_RECT.centery - 14),
        (RES_LEFT_RECT.centerx - 8, RES_LEFT_RECT.centery),
        (RES_LEFT_RECT.centerx + 8, RES_LEFT_RECT.centery + 14),
    ])

    # Right arrow button
    hovered = RES_RIGHT_RECT.collidepoint(mouse_pos)
    fill = (30, 50, 90) if not hovered else (45, 75, 130)
    pygame.draw.rect(screen, fill, RES_RIGHT_RECT, border_radius=10)
    pygame.draw.rect(screen, (80, 180, 255), RES_RIGHT_RECT, 2, border_radius=10)
    pygame.draw.polygon(screen, (255, 255, 255), [
        (RES_RIGHT_RECT.centerx - 8, RES_RIGHT_RECT.centery - 14),
        (RES_RIGHT_RECT.centerx + 8, RES_RIGHT_RECT.centery),
        (RES_RIGHT_RECT.centerx - 8, RES_RIGHT_RECT.centery + 14),
    ])

    # Value panel [HD]
    panel = pygame.Surface((RES_VALUE_RECT.width, RES_VALUE_RECT.height), pygame.SRCALPHA)
    panel.fill((20, 40, 90, 200))
    screen.blit(panel, RES_VALUE_RECT.topleft)
    pygame.draw.rect(screen, (80, 180, 255), RES_VALUE_RECT, 3, border_radius=14)

    value = font.render(settings.CURRENT_RESOLUTION, True, (255, 255, 255))
    screen.blit(value, value.get_rect(center=RES_VALUE_RECT.center))


def handle_event(event):
    # Key 'Esc' also works to go back 
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return "back"

    if event.type == pygame.MOUSEBUTTONDOWN:
        if BACK_RECT.collidepoint(event.pos):
            audio.play_sound("button_click") # play click sfx when button gets clicked
            return "back"


        # Handler for the Change of resolution in settings
        if RES_LEFT_RECT.collidepoint(event.pos) or RES_RIGHT_RECT.collidepoint(event.pos):
            audio.play_sound("button_click") # play click sfx when button gets clicked
            
            # Sswitch between availeable resolutions [HD, FHD] for now
            new_resolution = "FHD" if settings.CURRENT_RESOLUTION == "HD" else "HD"
            settings.set_resolution(new_resolution)
            rebuild_layout()
            return "switch_resolution" # state for 'switch resolution' (applied in main.py)

    return None

# Function for the 'switch resolution'. to re-scale the settings menu layout
def rebuild_layout():
    global BACK_RECT, RES_LABEL_POS, RES_VALUE_RECT, RES_LEFT_RECT, RES_RIGHT_RECT, back_btn_img

    # All the following values are about new possitioning of the rectangles (whenver the resolution is re-scaled)

    BACK_RECT = pygame.Rect(20, 20, 80, 80)

    center_x = settings.WIDTH // 2
    y = settings.HEIGHT // 2

    RES_LABEL_POS = (center_x - 260, y)

    RES_VALUE_RECT = pygame.Rect(0, 0, 140, 60)
    RES_VALUE_RECT.center = (center_x + 140, y)

    RES_LEFT_RECT = pygame.Rect(0, 0, 60, 60)
    RES_LEFT_RECT.midright = (RES_VALUE_RECT.left - 15, RES_VALUE_RECT.centery)

    RES_RIGHT_RECT = pygame.Rect(0, 0, 60, 60)
    RES_RIGHT_RECT.midleft = (RES_VALUE_RECT.right + 15, RES_VALUE_RECT.centery)

    # Reload globals to be loaded with the 'correct' no scaled sizes
    back_btn_img = None
