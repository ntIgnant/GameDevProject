import os

import pygame

WIDTH = 1280
HEIGHT = 720

pygame.init()
background_color = (252, 252, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load(os.path.join("Assets", "Background", "demo3.png"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.display.set_caption('Game name')
clock = pygame.time.Clock()
font1 = pygame.font.SysFont('Comic Sans MS', 50)
font2 = pygame.font.SysFont('Comic Sans MS', 30)
START_RECT = pygame.Rect(0, 0, 320, 50)

def draw_level():
    screen.blit(background, (0,0))

def draw_main_screen():
    screen.fill(background_color)

    # main rectangle
    title_rect = pygame.Rect(0, 0, 640, 100)
    title_rect.center = (WIDTH // 2, HEIGHT // 3)
    pygame.draw.rect(screen, (0, 128, 254), title_rect)

    # start rectangle
    START_RECT.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0, 128, 254), START_RECT)

    # main text
    main_menu_text = font1.render("MAIN MENU", True, (0, 0, 0))
    main_menu_text_rect = main_menu_text.get_rect(center=title_rect.center)
    screen.blit(main_menu_text, main_menu_text_rect)

    # start text
    start_text = font2.render("Start", True, (0, 0, 0))
    start_text_rect = start_text.get_rect(center=START_RECT.center)
    screen.blit(start_text, start_text_rect)

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    pygame.display.update()


running = True
main_menu = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if START_RECT.collidepoint(event.pos):
                main_menu = False

    if main_menu:
        draw_main_screen()
    else:
        draw_level()

    pygame.display.update()

    clock.tick(60)
pygame.quit()
