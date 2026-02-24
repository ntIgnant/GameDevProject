import pygame
from .settings import WIDTH, HEIGHT

background_color = (252, 252, 255)

def draw_main_screen(screen):
    font1 = pygame.font.SysFont('Comic Sans MS', 50)
    font2 = pygame.font.SysFont('Comic Sans MS', 30)

START_RECT = pygame.Rect(0, 0, 320, 50)

def draw_main_screen(screen):
    font1 = pygame.font.SysFont('Comic Sans MS', 50)
    font2 = pygame.font.SysFont('Comic Sans MS', 30)

    screen.fill(background_color)

    title_rect = pygame.Rect(0, 0, 640, 100)
    title_rect.center = (WIDTH // 2, HEIGHT // 3)
    pygame.draw.rect(screen, (0, 128, 254), title_rect)

    START_RECT.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0, 128, 254), START_RECT)

    main_menu_text = font1.render("MAIN MENU", True, (0, 0, 0))
    screen.blit(main_menu_text, main_menu_text.get_rect(center=title_rect.center))

    start_text = font2.render("Start", True, (0, 0, 0))
    screen.blit(start_text, start_text.get_rect(center=START_RECT.center))