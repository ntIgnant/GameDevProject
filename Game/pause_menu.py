import os
import pygame

import Game.settings as settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "pause_menu")

WINDOW_PATH = os.path.join(ASSETS_DIR, "Window.png")
HEADER_PATH = os.path.join(ASSETS_DIR, "Header.png")
RESUME_PATH = os.path.join(ASSETS_DIR, "Ok_BTN.png")
MENU_PATH = os.path.join(ASSETS_DIR, "Menu_BTN.png")

#starts as None because the PNG files are loaded later in load_assets()
window_raw = None
header_raw = None
resume_raw = None
menu_raw = None

#starts as None because the scaled versions are only created
#after rebuild_layout() knows the current screen size
window_img = None
header_img = None
resume_img = None
menu_img = None

#start as empty rectangles so the variables already exist before
#we calculate the real position and size of each UI element
window_rect = pygame.Rect(0, 0, 0, 0)
header_rect = pygame.Rect(0, 0, 0, 0)
resume_rect = pygame.Rect(0, 0, 0, 0)
menu_rect = pygame.Rect(0, 0, 0, 0)
pause_rect = pygame.Rect(0, 0, 0, 0)

title_font = None
hint_font = None
countdown_font = None
screen_size = (0, 0)


def load_assets():
    global window_raw, header_raw, resume_raw, menu_raw

    #load the original images once from disk
    #after this, the game reuses them and only rescales them when needed
    if window_raw is None:
        window_raw = pygame.image.load(WINDOW_PATH).convert_alpha()
        header_raw = pygame.image.load(HEADER_PATH).convert_alpha()
        resume_raw = pygame.image.load(RESUME_PATH).convert_alpha()
        menu_raw = pygame.image.load(MENU_PATH).convert_alpha()

    rebuild_layout()


def rebuild_layout():
    global window_img, header_img, resume_img, menu_img
    global window_rect, header_rect, resume_rect, menu_rect, pause_rect
    global title_font, hint_font, countdown_font, screen_size

    if window_raw is None:
        return

    #one scale value keeps the UI roughly proportional on different resolutions
    scale = min(settings.WIDTH / 1280, settings.HEIGHT / 720)

    #the pause window art is quite large, so resize it to fit the current screen
    panel_scale = min(
        (settings.WIDTH * 0.42) / window_raw.get_width(),
        (settings.HEIGHT * 0.76) / window_raw.get_height(),
    )
    panel_scale = max(panel_scale, 0.35)

    panel_width = int(window_raw.get_width() * panel_scale)
    panel_height = int(window_raw.get_height() * panel_scale)
    window_img = pygame.transform.smoothscale(window_raw, (panel_width, panel_height))
    window_rect = window_img.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))

    #the PAUSE header is scaled separately so it fits nicely near the top of the window
    header_width = int(window_rect.width * 0.62)
    header_height = int(header_raw.get_height() * (header_width / header_raw.get_width()))
    header_img = pygame.transform.smoothscale(header_raw, (header_width, header_height))
    header_rect = header_img.get_rect(
        center=(window_rect.centerx, window_rect.top + int(window_rect.height * 0.07))
    )

    #these values decide the size and spacing of the Resume/Menu buttons
    button_size = max(92, int(108 * scale))
    button_gap = max(28, int(34 * scale))
    button_y = window_rect.top + int(window_rect.height * 0.62)
    button_offset = (button_size + button_gap) // 2

    resume_img = pygame.transform.smoothscale(resume_raw, (button_size, button_size))
    menu_img = pygame.transform.smoothscale(menu_raw, (button_size, button_size))
    resume_rect = resume_img.get_rect(center=(window_rect.centerx - button_offset, button_y))
    menu_rect = menu_img.get_rect(center=(window_rect.centerx + button_offset, button_y))

    #this is the small pause icon shown during gameplay in the top-left corner
    pause_size = max(44, int(54 * scale))
    pause_margin = max(16, int(22 * scale))
    pause_rect = pygame.Rect(
        pause_margin,
        pause_margin,
        pause_size,
        pause_size,
    )

    title_font = pygame.font.SysFont("Orbitron", max(20, int(26 * scale)), bold=True)
    hint_font = pygame.font.SysFont("Orbitron", max(14, int(18 * scale)), bold=True)
    countdown_font = pygame.font.SysFont("Orbitron", max(120, int(170 * scale)), bold=True)
    screen_size = (settings.WIDTH, settings.HEIGHT)


def ensure_ready():
    #If the assets were never loaded, load them now
    #If the resolution changed, rebuild all sizes and positions
    if window_raw is None:
        load_assets()
    elif screen_size != (settings.WIDTH, settings.HEIGHT):
        rebuild_layout()


def pause_button_hit(pos):
    ensure_ready()
    #used by level_1.py detects clicks on the small pause button
    return pause_rect.collidepoint(pos)


def overlay_action(pos):
    ensure_ready()
    #used by level_1.py to decide which pause menu button was clicked
    if resume_rect.collidepoint(pos):
        return "resume"
    if menu_rect.collidepoint(pos):
        return "menu"
    return None


def draw_pause_button(screen):
    ensure_ready()
    hovered = pause_rect.collidepoint(pygame.mouse.get_pos())
    fill_color = (15, 31, 56) if hovered else (10, 23, 44)
    border_color = (110, 216, 255) if hovered else (78, 184, 230)

    #draw the small pause box
    pygame.draw.rect(screen, fill_color, pause_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, pause_rect, 2, border_radius=12)

    #draw the two bars that make the icon look like a pause symbol
    bar_width = max(5, pause_rect.width // 8)
    bar_height = int(pause_rect.height * 0.44)
    bar_y = pause_rect.y + (pause_rect.height - bar_height) // 2
    left_x = pause_rect.centerx - bar_width - 4
    right_x = pause_rect.centerx + 4

    pygame.draw.rect(screen, (240, 248, 255), (left_x, bar_y, bar_width, bar_height), border_radius=4)
    pygame.draw.rect(screen, (240, 248, 255), (right_x, bar_y, bar_width, bar_height), border_radius=4)


def draw_overlay(screen):
    ensure_ready()
    mouse_pos = pygame.mouse.get_pos()

    #dark transparent layers make the gameplay behind the menu feel paused
    screen.blit(make_layer(screen.get_size(), (7, 12, 24, 165)), (0, 0))
    screen.blit(make_layer(window_rect.size, (0, 0, 0, 70)), window_rect.move(0, 10).topleft)

    #draw the pause window and its header
    screen.blit(window_img, window_rect.topleft)
    screen.blit(header_img, header_rect.topleft)

    subtitle = title_font.render("Choose an action", True, (228, 240, 255))
    subtitle_rect = subtitle.get_rect(
        center=(window_rect.centerx, window_rect.top + int(window_rect.height * 0.30))
    )
    screen.blit(subtitle, subtitle_rect)

    #draw both action buttons using the same helper so their style stays consistent
    draw_action_button(screen, resume_img, resume_rect, "Resume", mouse_pos, primary=True)
    draw_action_button(screen, menu_img, menu_rect, "Menu", mouse_pos)

    hint = hint_font.render("Press Esc to resume with countdown", True, (203, 221, 242))
    hint_rect = hint.get_rect(
        center=(window_rect.centerx, window_rect.bottom - int(window_rect.height * 0.16))
    )
    screen.blit(hint, hint_rect)


def draw_resume_countdown(screen, seconds_left):
    ensure_ready()
    screen.blit(make_layer(screen.get_size(), (4, 8, 18, 145)), (0, 0))

    #this is shown after pressing resume so the player gets a short warning
    #before gameplay starts moving again
    title = title_font.render("Resuming", True, (225, 239, 255))
    screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 90)))

    #Drawing the number twice creates a simple outline effect with
    #blue copies around the outside, white text in the center
    text = countdown_font.render(str(seconds_left), True, (255, 255, 255))
    outline = countdown_font.render(str(seconds_left), True, (28, 117, 255))
    rect = text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 24))

    for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4)]:
        screen.blit(outline, rect.move(dx, dy))
    screen.blit(text, rect)


def draw_action_button(screen, image, rect, label, mouse_pos, primary=False):
    #If the mouse is over a button, draw a glow behind it
    glow_color = (130, 232, 255, 75) if primary else (106, 219, 255, 55)
    if rect.collidepoint(mouse_pos):
        glow_rect = rect.inflate(18, 18)
        glow = make_layer(glow_rect.size, (0, 0, 0, 0))
        pygame.draw.ellipse(glow, glow_color, glow.get_rect())
        screen.blit(glow, glow_rect.topleft)

    #draw the button image and its text label
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
