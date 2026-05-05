import os
import pygame
import Game.settings as settings
import Game.audio as audio


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STORY_DIR = os.path.join(BASE_DIR, "Assets", "Story")

# Story 'scenes' paths
# Maybe add a third one for lvl2 -> lvl3 transition
SCENE_PATHS = {
    "scene_01": os.path.join(STORY_DIR, "scene_01.jpg"),
    "scene_02": os.path.join(STORY_DIR, "scene_02.jpg"),
}

# Some globals here

raw_scene_images = {} # this set will contain the actuall images (.jpgs) from the paths to use them in the loader
scene_images = {} # set containing the scaled images (correct size and format for pygame screen to show them)
current_scene = None
next_action = None

# This is for the 'skip button' object
skip_rect = pygame.Rect(0, 0, 0, 0)
skip_font = None

# flags and configs for 'fade out' after 'skip' button is pressed
is_fading_out = False
fade_alpha = 0
FADE_SPEED = 170

# This function loads the actual images (.jps in paths) and resize them to be represented in the pygame screen
def load_assets():
    global raw_scene_images

    raw_scene_images = {}

    # Scale each of the images in the directionary 'SCENE_PATHS'
    for scene_name in SCENE_PATHS:
        image_path = SCENE_PATHS[scene_name]
        raw_scene_images[scene_name] = pygame.image.load(image_path).convert() # resize 'scale' image

    rebuild_layout()

# Builds the layou (everything that is on the screen) with the properly scalled images and created 'skip' button
def rebuild_layout():
    global scene_images, skip_rect, skip_font

    if len(raw_scene_images) == 0:
        return

    scene_images = {}

    for scene_name in raw_scene_images:
        original_image = raw_scene_images[scene_name]
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        # Scale the images (raw .jpgs) based on the HEIGHT and WIDTH values in settings.py to be scalled properly for pygame screeen
        width_scale = settings.WIDTH / original_width
        height_scale = settings.HEIGHT / original_height
        scale = min(width_scale, height_scale)

        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        scene_images[scene_name] = pygame.transform.smoothscale(
            original_image,
            (new_width, new_height),
        )

    # The following are configs for the 'skip' button object and text

    # Rectangle shape values
    button_width = int(settings.WIDTH * 0.14)
    button_height = int(settings.HEIGHT * 0.07)
    button_margin = int(settings.WIDTH * 0.035)

    skip_rect = pygame.Rect(0, 0, button_width, button_height)
    skip_rect.right = settings.WIDTH - button_margin
    skip_rect.bottom = settings.HEIGHT - button_margin

    # Config for text/font for the 'skip' text
    font_size = max(26, int(settings.HEIGHT * 0.045))
    skip_font = pygame.font.SysFont(None, font_size, bold=True)


# This function is the 'main' one to play the storyboards
# it plays the story board based on the current 'last' scene, sets the fade effect and stops the music
# NOTE: maybe we should add a music or sound effect here
def start_scene(scene_name, action_after_skip):
    global current_scene, next_action, is_fading_out, fade_alpha

    if len(raw_scene_images) == 0:
        load_assets()

    current_scene = scene_name
    next_action = action_after_skip
    is_fading_out = False # flag for 'fade out' effect after 'skip' is pressed
    fade_alpha = 0

    audio.stop_music()


def handle_event(event):
    global is_fading_out

    if is_fading_out:
        return None

    # This handles the 'skip button pressing' so the scenes can be skipped with one of these keys
    # [ESC, SPACE, ENTER] for better user intuition
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            is_fading_out = True # Trigger the 'fade out' effect by changinf the status flag

    # Or 'skip' by clicking the button
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and skip_rect.collidepoint(event.pos):
            audio.play_sound("button_click")
            is_fading_out = True

    return None


def update(dt):
    global fade_alpha

    if not is_fading_out:
        return None

    fade_alpha = fade_alpha + FADE_SPEED * dt

    if fade_alpha >= 255:
        fade_alpha = 255
        return next_action

    return None

# This shows everything on the pygame programm screeen, so curre
def draw(screen):
    screen.fill((0, 0, 0))

    scene_image = scene_images.get(current_scene)
    if scene_image is not None:
        screen_rect = screen.get_rect()
        image_rect = scene_image.get_rect()
        image_rect.center = screen_rect.center
        screen.blit(scene_image, image_rect)

    mouse_pos = pygame.mouse.get_pos()

    if skip_rect.collidepoint(mouse_pos):
        button_color = (230, 230, 230)
    else:
        button_color = (190, 190, 190)

    pygame.draw.rect(screen, (10, 12, 18), skip_rect, border_radius=8)
    pygame.draw.rect(screen, button_color, skip_rect, 2, border_radius=8)

    if skip_font is not None:
        label = skip_font.render("SKIP", True, button_color)
        label_rect = label.get_rect()
        label_rect.center = skip_rect.center
        screen.blit(label, label_rect)

    if is_fading_out and fade_alpha > 0:
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(fade_alpha)))
        screen.blit(fade, (0, 0))
