import os
import pygame
import Game.settings as settings # Overall game settings (res, fps, ...)
import Game.audio as audio # SFX

# Paths to background and other assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Menu")
BG_PATH = os.path.join(ASSETS_DIR, "BG.png") # Different background image for the menu_settings
BACK_BTN_PATH = os.path.join(ASSETS_DIR, "Backward_BTN.png")

# Aspect ration and size of the 'back' button
BACK_RECT = pygame.Rect(20, 20, 80, 80) # Button placement on screen (now top left)
background_img = None
back_btn_img = None

# Rectangles for the audio settings
VOLUME_STEP = 0.10
MUSIC_LABEL_POS = (0, 0)
MUSIC_VALUE_RECT = pygame.Rect(0, 0, 140, 60) # Rectangle for % of Music Volume
MUSIC_LEFT_RECT = pygame.Rect(0, 0, 60, 60) # Left Button Music Volume
MUSIC_RIGHT_RECT = pygame.Rect(0, 0, 60, 60) # Right Button Music Volume 

SFX_LABEL_POS = (0, 0)
SFX_VALUE_RECT = pygame.Rect(0, 0, 140, 60) # Rectangle for % of SFX Volume
SFX_LEFT_RECT = pygame.Rect(0, 0, 60, 60) # Left Button SFX Volume
SFX_RIGHT_RECT = pygame.Rect(0, 0, 60, 60) # Right Button SFX Volume

MUTE_MUSIC_LABEL_POS = (0, 0)
MUTE_MUSIC_RECT = pygame.Rect(0, 0, 160, 54) # on/off Mute
MUTE_SFX_LABEL_POS = (0, 0)
MUTE_SFX_RECT = pygame.Rect(0, 0, 160, 54) # on/off Mute SFX
MUTE_ALL_LABEL_POS = (0, 0)
MUTE_ALL_RECT = pygame.Rect(0, 0, 160, 54) # on/off Mute Master

# Loads the assets used for the menu, and aplies scalation for some (mainly for the buttons)
def load_settings_assets():
    global background_img, back_btn_img

    background_img = pygame.image.load(BG_PATH).convert()
    background_img = pygame.transform.smoothscale(background_img, (settings.WIDTH, settings.HEIGHT))

    back_btn_img = pygame.image.load(BACK_BTN_PATH).convert_alpha()
    back_btn_img = pygame.transform.smoothscale(back_btn_img,(BACK_RECT.width, BACK_RECT.height))

# With the already loaded (and scaled assets)
# This function draws the whole UI for the settings menu
# Placements for all the used assets, background, buttons, etc
def draw(screen):
    global background_img, back_btn_img

    if background_img is None:
        load_settings_assets()

    screen.blit(background_img, (0, 0))

    if back_btn_img is None:
        load_settings_assets()

    # Title and text settings
    font_title = pygame.font.SysFont("Orbitron", 60, bold=True)
    title = font_title.render("SETTINGS", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, 150)))

    # 'Back' button settings, to go back to main menu
    screen.blit(back_btn_img, BACK_RECT.topleft)

    font = pygame.font.SysFont("Orbitron", 28, bold=True)
    mouse_pos = pygame.mouse.get_pos()

    _draw_volume_row(
        screen,
        font,
        mouse_pos,
        "MUSIC VOLUME",
        MUSIC_LABEL_POS,
        MUSIC_LEFT_RECT,
        MUSIC_VALUE_RECT,
        MUSIC_RIGHT_RECT,
        audio.music_volume,
    )
    _draw_volume_row(
        screen,
        font,
        mouse_pos,
        "SFX VOLUME",
        SFX_LABEL_POS,
        SFX_LEFT_RECT,
        SFX_VALUE_RECT,
        SFX_RIGHT_RECT,
        audio.sfx_volume,
    )
    _draw_toggle_row(
        screen,
        font,
        mouse_pos,
        "MUTE MUSIC",
        MUTE_MUSIC_LABEL_POS,
        MUTE_MUSIC_RECT,
        audio.music_muted,
    )
    _draw_toggle_row(
        screen,
        font,
        mouse_pos,
        "MUTE SFX",
        MUTE_SFX_LABEL_POS,
        MUTE_SFX_RECT,
        audio.sfx_muted,
    )
    _draw_toggle_row(
        screen,
        font,
        mouse_pos,
        "MUTE ALL",
        MUTE_ALL_LABEL_POS,
        MUTE_ALL_RECT,
        audio.master_muted,
    )


# Helper function that draws the arrow buttons for the options (mainly for volumes %)
def _draw_arrow_button(screen, rect, mouse_pos, direction):
    hovered = rect.collidepoint(mouse_pos)
    fill = (30, 50, 90) if not hovered else (45, 75, 130) # Style to apply when it toggles to the 'ON' Option (Green color for now)
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, (80, 180, 255), rect, 2, border_radius=10)

    # The following are the polygons for the arrow buttons

    # Left direction button polygon
    if direction == "left":
        points = [
            (rect.centerx + 8, rect.centery - 14),
            (rect.centerx - 8, rect.centery),
            (rect.centerx + 8, rect.centery + 14),
        ]
    
    # Right direction button polygon
    else:
        points = [
            (rect.centerx - 8, rect.centery - 14),
            (rect.centerx + 8, rect.centery),
            (rect.centerx - 8, rect.centery + 14),
        ]
    pygame.draw.polygon(screen, (255, 255, 255), points)


# Helper function to draw the inner box for the volume %s
def _draw_value_panel(screen, font, rect, text):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((20, 40, 90, 200)) # Box color (blue for now)
    screen.blit(panel, rect.topleft)
    pygame.draw.rect(screen, (80, 180, 255), rect, 3, border_radius=14)

    value = font.render(text, True, (255, 255, 255))
    screen.blit(value, value.get_rect(center=rect.center))


# Helper function that draws the whole row (container) for the volumes (music and sfx)
# Basically takes left/right arrow, colored percentage box, and lables (text) to build the row
def _draw_volume_row(screen, font, mouse_pos, label_text, label_pos, left_rect, value_rect, right_rect, volume):
    label = font.render(label_text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(midleft=label_pos))

    _draw_arrow_button(screen, left_rect, mouse_pos, "left")
    _draw_arrow_button(screen, right_rect, mouse_pos, "right")
    _draw_value_panel(screen, font, value_rect, f"{round(volume * 100):d}%")


def _draw_toggle_row(screen, font, mouse_pos, label_text, label_pos, button_rect, enabled):
    label = font.render(label_text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(midleft=label_pos))

    hovered = button_rect.collidepoint(mouse_pos)

    # Blue and greeen color for the option toggle
    # If it is OFF, border color of box is blue
    # if it is ON, border color of box is green

    # Toggle options colors
    fill = (30, 50, 90) if not hovered else (45, 75, 130)
    border = (80, 255, 160) if enabled else (80, 180, 255)
    
    pygame.draw.rect(screen, fill, button_rect, border_radius=14)
    pygame.draw.rect(screen, border, button_rect, 3, border_radius=14)

    # Toggle volume options on/of
    text = "ON" if enabled else "OFF"
    value = font.render(text, True, (255, 255, 255))
    screen.blit(value, value.get_rect(center=button_rect.center))

# Handle behavior (turn up/down volume, mute, unmute, etc) based on user action in the menu
# This works as the orchestrator of the menu settings logic
# NOTE: Based on user option, the function will change the values of the music/sfx in the audio.py file
def handle_event(event):
    # Key 'Esc' also works to go back 
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return "back"

    if event.type == pygame.MOUSEBUTTONDOWN:
        if BACK_RECT.collidepoint(event.pos):
            audio.play_sound("button_click") # play click sfx when button gets clicked
            return "back"


        if MUSIC_LEFT_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.music_volume = max(0.0, audio.music_volume - VOLUME_STEP)
            audio.apply_audio_settings()
        elif MUSIC_RIGHT_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.music_volume = min(1.0, audio.music_volume + VOLUME_STEP)
            audio.apply_audio_settings()
        elif SFX_LEFT_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.sfx_volume = max(0.0, audio.sfx_volume - VOLUME_STEP)
            audio.apply_audio_settings()
        elif SFX_RIGHT_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.sfx_volume = min(1.0, audio.sfx_volume + VOLUME_STEP)
            audio.apply_audio_settings()
        elif MUTE_MUSIC_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.music_muted = not audio.music_muted
            audio.apply_audio_settings()
        elif MUTE_SFX_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.sfx_muted = not audio.sfx_muted
            audio.apply_audio_settings()
        elif MUTE_ALL_RECT.collidepoint(event.pos):
            audio.play_sound("button_click")
            audio.master_muted = not audio.master_muted
            audio.apply_audio_settings()

    return None

# Function to re-scale the settings menu layout
def rebuild_layout():
    global BACK_RECT, background_img, back_btn_img
    global MUSIC_LABEL_POS, MUSIC_VALUE_RECT, MUSIC_LEFT_RECT, MUSIC_RIGHT_RECT
    global SFX_LABEL_POS, SFX_VALUE_RECT, SFX_LEFT_RECT, SFX_RIGHT_RECT
    global MUTE_MUSIC_LABEL_POS, MUTE_MUSIC_RECT, MUTE_SFX_LABEL_POS, MUTE_SFX_RECT, MUTE_ALL_LABEL_POS, MUTE_ALL_RECT

    # All the following values are about new possitioning of the rectangles (whenver the resolution is re-scaled)

    BACK_RECT = pygame.Rect(20, 20, 80, 80)

    center_x = settings.WIDTH // 2
    start_y = int(settings.HEIGHT * 0.38)
    row_gap = int(78 * (settings.WIDTH / 1280))
    label_x = center_x - int(330 * (settings.WIDTH / 1280))
    value_x = center_x + int(145 * (settings.WIDTH / 1280))

    MUSIC_LABEL_POS = (label_x, start_y)
    MUSIC_VALUE_RECT = pygame.Rect(0, 0, 140, 60)
    MUSIC_VALUE_RECT.center = (value_x, start_y)
    MUSIC_LEFT_RECT = pygame.Rect(0, 0, 60, 60)
    MUSIC_LEFT_RECT.midright = (MUSIC_VALUE_RECT.left - 15, MUSIC_VALUE_RECT.centery)
    MUSIC_RIGHT_RECT = pygame.Rect(0, 0, 60, 60)
    MUSIC_RIGHT_RECT.midleft = (MUSIC_VALUE_RECT.right + 15, MUSIC_VALUE_RECT.centery)

    sfx_y = start_y + row_gap
    SFX_LABEL_POS = (label_x, sfx_y)
    SFX_VALUE_RECT = pygame.Rect(0, 0, 140, 60)
    SFX_VALUE_RECT.center = (value_x, sfx_y)
    SFX_LEFT_RECT = pygame.Rect(0, 0, 60, 60)
    SFX_LEFT_RECT.midright = (SFX_VALUE_RECT.left - 15, SFX_VALUE_RECT.centery)
    SFX_RIGHT_RECT = pygame.Rect(0, 0, 60, 60)
    SFX_RIGHT_RECT.midleft = (SFX_VALUE_RECT.right + 15, SFX_VALUE_RECT.centery)

    toggle_x = value_x
    mute_music_y = sfx_y + row_gap
    MUTE_MUSIC_LABEL_POS = (label_x, mute_music_y)
    MUTE_MUSIC_RECT = pygame.Rect(0, 0, 160, 54)
    MUTE_MUSIC_RECT.center = (toggle_x, mute_music_y)

    mute_sfx_y = mute_music_y + row_gap
    MUTE_SFX_LABEL_POS = (label_x, mute_sfx_y)
    MUTE_SFX_RECT = pygame.Rect(0, 0, 160, 54)
    MUTE_SFX_RECT.center = (toggle_x, mute_sfx_y)

    mute_all_y = mute_sfx_y + row_gap
    MUTE_ALL_LABEL_POS = (label_x, mute_all_y)
    MUTE_ALL_RECT = pygame.Rect(0, 0, 160, 54)
    MUTE_ALL_RECT.center = (toggle_x, mute_all_y)

    # Reload globals to be loaded with the 'correct' no scaled sizes
    background_img = None
    back_btn_img = None
