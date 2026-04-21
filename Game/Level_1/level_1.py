# Controller of Logic for Level 1
import math
import os
import pygame
import Game.settings as settings
from Game.player import Player
from Game.gun import GunProjectile
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames
from Game.obstacles import Obstacles
from Game.timer import Timer
from Game.camera import Camera
import Game.pause_menu as pause_menu

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
BASE_LEVEL_SIZE = settings.RESOLUTIONS["HD"]
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "Background", "demo2.png")

# Allowed area where the player/enemies can move | NOTE: This will be different depending on the level (corner boxes differ between background imgs)
LEVEL_1_AREA_CONFIG = {
    # Area for the player/enemies to move (big square)
    "walkable_area": [96, 170, 1095, 430],

    # Collision-only blockers for the background corner objects.
    # Each item is [offset_x, offset_y, width, height], measured from the walkable area's top-left corner.
    "corner_objects": [
        # Top left corner
        [0, 0, 210, 80],

        # Top right corner
        [900, -30, 190, 80],

        # Bottom left corner
        [0, 280, 100, 100],

        # Bottom right corner
        [975, 280, 120, 180],
    ]
}

LEVEL_AREA = pygame.Rect(0, 0, 0, 0)

DEV_MODE = False # This boolean is to view the restricted walkable-areas and coordinates of mouse in the game (for developement only) | False by default
background = None
player = None
obstacle = None
enemies = []
bullets = []
walk_frames = []
timer = Timer(minutes = 2)
camera = Camera()
debug_font = None
CORNER_DEBUG_COLOR = (220, 70, 70, 153) # For development only, to bisualize the restricted areas of the level
is_paused = False
resume_countdown = 0.0

# This is the 'damange rate' of the enemy to the player
# Lower = Faster damage
contact_damage_cooldown = 0.02
contact_damage_timer = 0.0

# 'damage rate' of one player's bullet. Used to damange enemy
# Higher number -> more damange
bullet_damage = 10

# This function checks for collision between the sec_enemy and the player, but for the comparision
# it adds 'tolerance' to the enemy area to make sure player and enemy collide. This to make sure the damage is received
# to the player.
def rects_touch_or_overlap(rect_a, rect_b, tolerance=1):
    expanded_a = rect_a.inflate(tolerance * 2, tolerance * 2)
    return expanded_a.colliderect(rect_b)

# Function to build the 'restricted areas' for the corner objects of the map (those corner boxes)
def scale_level_rect(rect_values):
    x, y, width, height = rect_values
    return pygame.Rect(x, y, width, height)

def rebuild_level_area():
    global LEVEL_AREA

    LEVEL_AREA = scale_level_rect(LEVEL_1_AREA_CONFIG["walkable_area"])

def build_corner_object_rects():
    rects = []
    for offset_x, offset_y, width, height in LEVEL_1_AREA_CONFIG["corner_objects"]:
        scaled_rect = scale_level_rect((offset_x, offset_y, width, height))
        rects.append(
            pygame.Rect(
                LEVEL_AREA.left + scaled_rect.x,
                LEVEL_AREA.top + scaled_rect.y,
                scaled_rect.width,
                scaled_rect.height,
            )
        )
    return rects

# Load Resources to initialize the level (background, ... structures should go here as well)
def load_assets():
    """Call after pygame display is initialized."""
    global background, walk_frames, debug_font

    raw_background = pygame.image.load(BACKGROUND_PATH).convert()
    background = pygame.transform.smoothscale(raw_background, BASE_LEVEL_SIZE)

    walk_frames = load_walk_frames()
    debug_font = pygame.font.SysFont(None, 24)

def rebuild_layout():
    global background

    rebuild_level_area()
    camera.width = settings.WIDTH
    camera.height = settings.HEIGHT
    camera.zoom = camera.base_zoom * min(
        settings.WIDTH / BASE_LEVEL_SIZE[0],
        settings.HEIGHT / BASE_LEVEL_SIZE[1],
    )
    if background is not None:
        raw_background = pygame.image.load(BACKGROUND_PATH).convert()
        background = pygame.transform.smoothscale(raw_background, BASE_LEVEL_SIZE)
    if obstacle is not None:
        obstacle.set_corner_blockers(build_corner_object_rects())
    if player is not None:
        player.rect.clamp_ip(LEVEL_AREA)

# Creates the objects Player and Enemy (just secondary enemy for now) when the level starts
def start_level():
    """Call once when entering Level 1."""
    global player, enemies, obstacle, bullets, is_paused, resume_countdown, contact_damage_timer

    rebuild_level_area()
    player = Player(LEVEL_AREA.center)
    enemy_spawn = (
        LEVEL_AREA.left + 100,
        LEVEL_AREA.top + 100,
    ) # Hardcoded area where the secondary enemy spawns
    enemies = [SecEnemyLev1(enemy_spawn, walk_frames),] # a single secondary enemy (for now)
    bullets = []
    obstacle = Obstacles()
    obstacle.spawn(area_rect=LEVEL_AREA)
    obstacle.set_corner_blockers(build_corner_object_rects())
    is_paused = False
    resume_countdown = 0.0
    contact_damage_timer = 0.0


def start_resume_countdown():
    global is_paused, resume_countdown

    is_paused = False
    resume_countdown = 3.0


def handle_pause_input(events):
    global is_paused, resume_countdown

    if resume_countdown > 0:
        return None

    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if is_paused:
                start_resume_countdown()
            else:
                is_paused = True
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_paused:
                action = pause_menu.overlay_action(event.pos)
                if action == "resume":
                    start_resume_countdown()
                elif action == "menu":
                    is_paused = False
                    resume_countdown = 0.0
                    return "menu"
                return None

            if pause_menu.pause_button_hit(event.pos):
                is_paused = True
                return None

    return None



def handle_level_event(event):
    if player:
        player.handle_event(event)

# Function to update the 'state' of the match after every movement
def update_level(dt, keys, events):
    global bullets, enemies, resume_countdown, contact_damage_timer

    if not player:
        return

    pause_action = handle_pause_input(events)
    if pause_action == "menu":
        return "menu"

    if is_paused:
        return None

    if resume_countdown > 0:
        resume_countdown = max(0.0, resume_countdown - dt)
        return None

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
            mouse_world = mouse_screen / camera.zoom + camera.offset
            player_pos = pygame.Vector2(player.rect.center)
            direction = mouse_world - player_pos

            if direction.length_squared() > 0:
                bullets.append(
                    GunProjectile(*player.rect.center, direction.normalize())
                )

    # Logic for bullet collision with sec-enemy (based on restricted areas)
    # If the bullet overlaps a restricted area 'e.g enemy area/off map ', then they disapear
    active_bullets = []
    for bullet in bullets:
        bullet.update(dt)
        if not LEVEL_AREA.colliderect(bullet.rect):
            continue

        # Check for collision between bullet and enemy, if there is collision, sec-enemy takes damange (value defined at bullet_damange)
        hit_enemy = False
        for enemy in enemies:
            if bullet.rect.colliderect(enemy.rect):
                enemy.take_damage(bullet_damage) # Update enemy health (take damange)
                hit_enemy = True
                break

        if hit_enemy:
            continue

        active_bullets.append(bullet)
    bullets = active_bullets

    timer.update(events)
    player.update(dt, keys, obstacle, [enemy.rect for enemy in enemies], LEVEL_AREA)
    camera.update(player)

    if contact_damage_timer > 0:
        contact_damage_timer = max(0.0, contact_damage_timer - dt)

    for e in enemies:
        e.update(dt, player.rect.center, obstacle, player.rect, LEVEL_AREA)

    # If enemy health <= 0, enemy is dead and will disapear (restricted areas will be ignored)
    enemies = [enemy for enemy in enemies if enemy.is_alive()]
    
    enemy_touching_player = any(rects_touch_or_overlap(enemy.rect, player.rect) for enemy in enemies)
    if enemy_touching_player and contact_damage_timer <= 0:
        player.take_damage(1)
        contact_damage_timer = contact_damage_cooldown

    # When the player health reaches 0, "game_over" flag is returned
    # This would trigger the 'Game Over Screen' in the main.py which works as the orchestrator
    if player.health <= 0 or timer.seconds <= 0:
        return "game_over"

def draw_level(screen):
    if background is None:
        return

    background_camera_frame = background.get_rect(topleft=(0,0))
    background_camera_frame = camera.apply(background_camera_frame)

    # zooming in and drawing the background
    background_frame_zoom = pygame.transform.scale(background, background_camera_frame.size)
    screen.blit(background_frame_zoom, background_camera_frame.topleft)

    if player:
        player.draw(screen, camera)

    for bullet in bullets:
        bullet.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)


    obstacle.draw(screen, camera)
    if DEV_MODE:
        draw_corner_blocker_overlay(screen)
        draw_debug_coordinates(screen)

    if is_paused:
        pause_menu.draw_overlay(screen)
    elif resume_countdown > 0:
        pause_menu.draw_resume_countdown(screen, max(1, math.ceil(resume_countdown)))
    else:
        pause_menu.draw_pause_button(screen)
        
    timer.draw(screen)

# Tool used to visualize limited areas for player/enemies during developement
def draw_corner_blocker_overlay(screen):
    if obstacle is None:
        return

    for rect in obstacle.corner_blockers:
        camera_rect = camera.apply(rect)
        overlay = pygame.Surface(camera_rect.size, pygame.SRCALPHA)
        overlay.fill(CORNER_DEBUG_COLOR)
        screen.blit(overlay, camera_rect.topleft)

# Tool used to visualize coordinates during developement (for the area limitarions configs)
def draw_debug_coordinates(screen):
    if debug_font is None:
        return

    mouse_screen_x, mouse_screen_y = pygame.mouse.get_pos()
    mouse_world_x = int((mouse_screen_x / camera.zoom) + camera.offset.x)
    mouse_world_y = int((mouse_screen_y / camera.zoom) + camera.offset.y)

    coord_text = debug_font.render(
        f"Screen: ({mouse_screen_x}, {mouse_screen_y})  World: ({mouse_world_x}, {mouse_world_y})",
        True,
        (255, 255, 255),
    )
    screen.blit(coord_text, (10, 10))
