import pygame
import Game.settings as settings # This is mainly for the resolution (HD, or FHD)


retry_rect = pygame.Rect(0, 0, 0, 0)
menu_rect = pygame.Rect(0, 0, 0, 0)
title_font = None
button_font = None
screen_size = (0, 0)


def rebuild_layout():
    global retry_rect, menu_rect, title_font, button_font, screen_size

    scale = min(settings.WIDTH / 1280, settings.HEIGHT / 720)

    button_width = max(220, int(280 * scale))
    button_height = max(56, int(72 * scale))
    gap = max(20, int(26 * scale))
    center_x = settings.WIDTH // 2
    first_y = int(settings.HEIGHT * 0.56)

    retry_rect = pygame.Rect(0, 0, button_width, button_height)
    retry_rect.center = (center_x, first_y)

    menu_rect = pygame.Rect(0, 0, button_width, button_height)
    menu_rect.center = (center_x, first_y + button_height + gap)

    title_font = pygame.font.SysFont("Orbitron", max(44, int(64 * scale)), bold=True)
    button_font = pygame.font.SysFont("Orbitron", max(22, int(30 * scale)), bold=True)
    screen_size = (settings.WIDTH, settings.HEIGHT)


def ensure_ready():
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

    screen.fill((0, 0, 0))

    # Main Title Text Style 
    title = title_font.render("Game Over", True, (235, 235, 235))
    title_rect = title.get_rect(center=(settings.WIDTH // 2, int(settings.HEIGHT * 0.30)))
    screen.blit(title, title_rect)

    # Buttons for Retry and Menu
    mouse_pos = pygame.mouse.get_pos()
    draw_button(screen, retry_rect, "Retry", mouse_pos, primary=True)
    draw_button(screen, menu_rect, "Main Menu", mouse_pos)


# Function for the styles of the buttons and text (black and white for now)
def draw_button(screen, rect, label, mouse_pos, primary=False):
    hovered = rect.collidepoint(mouse_pos)

    fill_color = (220, 220, 220) if primary else (165, 165, 165)
    if hovered:
        fill_color = (245, 245, 245) if primary else (200, 200, 200)

    text_color = (0, 0, 0)
    border_color = (255, 255, 255) if hovered else (110, 110, 110)

    pygame.draw.rect(screen, fill_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

    label_surface = button_font.render(label, True, text_color)
    label_rect = label_surface.get_rect(center=rect.center)
    screen.blit(label_surface, label_rect)
