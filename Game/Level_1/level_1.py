# Controller of Logic for Level 1
import os
import pygame
from Game.settings import WIDTH, HEIGHT
from Game.player import Player
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames
from Game.obstacles import Obstacles
from Game.timer import Timer
from Game.camera import Camera

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

background = None
player = None
obstacle = None
enemies = []
walk_frames = []
timer = Timer(minutes = 2)
camera = Camera()

# Load Resources to initialize the level (background, ... structures should go here as well)
def load_assets():
    """Call after pygame display is initialized."""
    global background, walk_frames

    background = pygame.image.load(os.path.join(ASSETS_DIR, "Background", "demo1.png")).convert() # Background image
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    walk_frames = load_walk_frames()

# Creates the objects Player and Enemy (just secondary enemy for now) when the level starts
def start_level():
    """Call once when entering Level 1."""
    global player, enemies, obstacle

    player = Player()
    enemies = [SecEnemyLev1((100, 100), walk_frames),] # a single secondary enemy (for now)
    obstacle = Obstacles()
    obstacle.spawn()



def handle_level_event(event):
    if player:
        player.handle_event(event)

# Function to update the 'state' of the match after every movement
def update_level(dt, keys, events):
    if not player:
        return
      
    timer.update(events)
    player.update(dt, keys, obstacle)
    camera.update(player)

    for e in enemies:
        e.update(dt, player.rect.center, obstacle)


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

    for e in enemies:
        e.draw(screen, camera)


    timer.draw(screen)
    obstacle.draw(screen, camera)
    pygame.display.flip()
