import os
import pygame

import Game.settings as settings
import Game.audio as audio


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Story")

SCENE_PATHS = {
    "scene_01": os.path.join(ASSETS_DIR, "scene_01.jpg"),
    "scene_02": os.path.join(ASSETS_DIR, "scene_02.jpg"),
}

raw_scene_images = {}
scene_images = {}
current_scene = None
next_action = None
skip_rect = pygame.Rect(0, 0, 0, 0)
skip_font = None
transition_active = False
transition_alpha = 0
TRANSITION_FADE_SPEED = 170


def load_assets():
    global raw_scene_images, skip_font

    raw_scene_images = {
        scene_name: pygame.image.load(path).convert()
        for scene_name, path in SCENE_PATHS.items()
    }
    skip_font = pygame.font.SysFont(None, max(26, int(settings.HEIGHT * 0.045)), bold=True)
    rebuild_layout()


def rebuild_layout():
    global scene_images, skip_rect, skip_font

    if not raw_scene_images:
        return

    scene_images = {}
    for scene_name, image in raw_scene_images.items():
        image_width, image_height = image.get_size()
        scale = min(settings.WIDTH / image_width, settings.HEIGHT / image_height)
        scaled_size = (int(image_width * scale), int(image_height * scale))
        scene_images[scene_name] = pygame.transform.smoothscale(image, scaled_size)

    button_width = int(settings.WIDTH * 0.14)
    button_height = int(settings.HEIGHT * 0.07)
    margin = int(settings.WIDTH * 0.035)
    skip_rect = pygame.Rect(0, 0, button_width, button_height)
    skip_rect.bottomright = (settings.WIDTH - margin, settings.HEIGHT - margin)
    skip_font = pygame.font.SysFont(None, max(26, int(settings.HEIGHT * 0.045)), bold=True)


def start_scene(scene_name, action_after_skip):
    global current_scene, next_action, transition_active, transition_alpha

    if not raw_scene_images:
        load_assets()

    current_scene = scene_name
    next_action = action_after_skip
    transition_active = False
    transition_alpha = 0
    audio.stop_music()


def start_transition():
    global transition_active

    if not transition_active:
        transition_active = True


def handle_event(event):
    if transition_active:
        return None

    if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
        start_transition()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if skip_rect.collidepoint(event.pos):
            audio.play_sound("button_click")
            start_transition()

    return None


def update(dt):
    global transition_alpha

    if not transition_active:
        return None

    transition_alpha = min(255, transition_alpha + TRANSITION_FADE_SPEED * dt)
    if transition_alpha >= 255:
        return next_action

    return None


def draw(screen):
    screen.fill((0, 0, 0))

    scene_image = scene_images.get(current_scene)
    if scene_image is not None:
        image_rect = scene_image.get_rect(center=screen.get_rect().center)
        screen.blit(scene_image, image_rect)

    mouse_pos = pygame.mouse.get_pos()
    button_color = (230, 230, 230) if skip_rect.collidepoint(mouse_pos) else (190, 190, 190)
    pygame.draw.rect(screen, (10, 12, 18), skip_rect, border_radius=8)
    pygame.draw.rect(screen, button_color, skip_rect, 2, border_radius=8)

    if skip_font is not None:
        label = skip_font.render("SKIP", True, button_color)
        screen.blit(label, label.get_rect(center=skip_rect.center))

    if transition_active and transition_alpha > 0:
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(transition_alpha)))
        screen.blit(fade, (0, 0))
