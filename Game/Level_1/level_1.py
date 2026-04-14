# Controller of Logic for Level 1
import os
import pygame
from Game.settings import WIDTH, HEIGHT
from Game.player import Player
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames
from Game.obstacles import Obstacles
from Game.timer import Timer
from Game.time_pickup import TimePickup
from Game.camera import Camera

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

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

LEVEL_AREA = pygame.Rect(*LEVEL_1_AREA_CONFIG["walkable_area"])


def build_corner_object_rects():
    rects = []
    for offset_x, offset_y, width, height in LEVEL_1_AREA_CONFIG["corner_objects"]:
        rects.append(
            pygame.Rect(
                LEVEL_AREA.left + offset_x,
                LEVEL_AREA.top + offset_y,
                width,
                height,
            )
        )
    return rects

DEV_MODE = False # This boolean is to view the restricted walkable-areas and coordinates of mouse in the game (for developement only) | False by default
background = None
player = None
obstacle = None
enemies = []
walk_frames = []
timer = Timer(minutes = 2)
camera = Camera()
debug_font = None
CORNER_DEBUG_COLOR = (220, 70, 70, 153) # For development only, to bisualize the restricted areas of the level
time_pickups = []
scheduled_time_pickups = []
TIME_PICKUP_BONUS_SECONDS = 15
TIME_PICKUP_SPAWN_DELAYS = [20.0, 40.0]


def build_time_pickups():
    candidate_positions = [
        LEVEL_AREA.center,
        (LEVEL_AREA.left + 220, LEVEL_AREA.centery),
        (LEVEL_AREA.right - 220, LEVEL_AREA.centery),
        (LEVEL_AREA.centerx, LEVEL_AREA.top + 120),
        (LEVEL_AREA.centerx, LEVEL_AREA.bottom - 120),
    ]

    pickups = []
    for center in candidate_positions:
        pickup = TimePickup(center, TIME_PICKUP_BONUS_SECONDS)
        if not any(pickup.rect.colliderect(rect) for rect in obstacle.collision_rects):
            pickups.append(pickup)
        if len(pickups) == len(TIME_PICKUP_SPAWN_DELAYS):
            break

    return pickups

# Load Resources to initialize the level (background, ... structures should go here as well)
def load_assets():
    """Call after pygame display is initialized."""
    global background, walk_frames, debug_font

    background = pygame.image.load(os.path.join(ASSETS_DIR, "Background", "demo2.png")).convert() # Background image
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    walk_frames = load_walk_frames()
    debug_font = pygame.font.SysFont(None, 24)

# Creates the objects Player and Enemy (just secondary enemy for now) when the level starts
def start_level():
    """Call once when entering Level 1."""
    global player, enemies, obstacle, time_pickups, scheduled_time_pickups

    player = Player()
    player.rect.clamp_ip(LEVEL_AREA)
    enemy_spawn = (LEVEL_AREA.left + 100, LEVEL_AREA.top + 100) # Hardcoded area where the secondary enemy spawns
    enemies = [SecEnemyLev1(enemy_spawn, walk_frames),] # a single secondary enemy (for now)
    obstacle = Obstacles()
    obstacle.spawn(area_rect=LEVEL_AREA)
    obstacle.set_corner_blockers(build_corner_object_rects())
    pickups = build_time_pickups()
    time_pickups = []
    scheduled_time_pickups = [
        {"pickup": pickup, "spawn_in": spawn_delay}
        for pickup, spawn_delay in zip(pickups, TIME_PICKUP_SPAWN_DELAYS)
    ]



def handle_level_event(event):
    if player:
        player.handle_event(event)

# Function to update the 'state' of the match after every movement
def update_level(dt, keys, events):
    global time_pickups, scheduled_time_pickups

    if not player:
        return
      
    timer.update(events)
    player.update(dt, keys, obstacle, LEVEL_AREA)
    camera.update(player)

    ready_pickups = []
    for scheduled_pickup in scheduled_time_pickups:
        scheduled_pickup["spawn_in"] = max(0.0, scheduled_pickup["spawn_in"] - dt)
        if scheduled_pickup["spawn_in"] <= 0:
            ready_pickups.append(scheduled_pickup)

    if ready_pickups:
        time_pickups.extend(item["pickup"] for item in ready_pickups)
        scheduled_time_pickups = [
            item for item in scheduled_time_pickups if item not in ready_pickups
        ]

    active_pickups = []
    for pickup in time_pickups:
        pickup.update(dt)
        if not pickup.try_collect(player.rect, timer):
            active_pickups.append(pickup)
    time_pickups = active_pickups

    for e in enemies:
        e.update(dt, player.rect.center, obstacle, LEVEL_AREA)


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

    for pickup in time_pickups:
        pickup.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)


    timer.draw(screen)
    obstacle.draw(screen, camera)
    if DEV_MODE:
        draw_corner_blocker_overlay(screen)
        draw_debug_coordinates(screen)
    pygame.display.flip()

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
