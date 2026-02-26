# Controller of Logic for Level 1
import os
import pygame
from Game.settings import WIDTH, HEIGHT
from Game.player import Player
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames
from Game.obstacles import Obstacles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

background = None
player = None
obstacle = None
enemies = []
walk_frames = []

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
def update_level(dt, keys):
    if not player:
        return

    player.update(dt, keys)
    for e in enemies:
        e.update(dt, player.rect.center)


def draw_level(screen):
    if background is None:
        return

    screen.blit(background, (0, 0))
    if player:
        player.draw(screen)

    for e in enemies:
        e.draw(screen)


    obstacle.draw(screen)