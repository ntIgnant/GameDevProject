# Controller of Logic for Level 1
import os
import pygame
import math
from Game.settings import WIDTH, HEIGHT
from Game.player import Player
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames
from Game.obstacles import Obstacles
from Game.timer import Timer
from Game.camera import Camera
from Game.gun import GunProjectile
from Game import pause_menu

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

background = None
player = None
obstacle = None
enemies = []
walk_frames = []
timer = None
camera = Camera()
bullets = []
is_paused = False
resume_countdown = 0.0

# Load Resources to initialize the level (background, ... structures should go here as well)
def load_assets():
    """Call after pygame display is initialized."""
    global background, walk_frames

    background = pygame.image.load(os.path.join(ASSETS_DIR, "Background", "demo1.png")).convert() # Background image
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    walk_frames = load_walk_frames()
    #Load pause-menu art once so the level can show it instantly in game.
    pause_menu.load_assets()

# Creates the objects Player and Enemy (just secondary enemy for now) when the level starts
def start_level():
    """Call once when entering Level 1."""
    global player, enemies, obstacle, bullets, timer, camera, is_paused, resume_countdown

    player = Player()
    enemies = [SecEnemyLev1((100, 100), walk_frames),] # a single secondary enemy (for now)
    obstacle = Obstacles()
    obstacle.spawn()
    timer = Timer(minutes = 2)
    camera = Camera()
    bullets = []
    is_paused = False
    resume_countdown = 0.0



def handle_level_event(event):
    if player:
        player.handle_event(event)


def _start_resume_countdown():
    global is_paused, resume_countdown

    #unpause immediately, but hold gameplay for 3 seconds in update_level().
    is_paused = False
    resume_countdown = 3.0


def _handle_pause_input(events):
    global is_paused, resume_countdown

    #ignore new pause input while the resume countdown is already running.
    if resume_countdown > 0:
        return None

    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if is_paused:
                _start_resume_countdown()
            else:
                is_paused = True
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_paused:
                #asks pause_menu.py which pause button was clicked.
                action = pause_menu.overlay_action(event.pos)
                if action == "resume":
                    _start_resume_countdown()
                elif action == "menu":
                    is_paused = False
                    resume_countdown = 0.0
                    #main.py uses this return value to go back to the main menu.
                    return "menu"
                return None

            if pause_menu.pause_button_hit(event.pos):
                is_paused = True
                return None

    return None

# Function to update the 'state' of the match after every movement
def update_level(dt, keys, events):
    global bullets, resume_countdown

    if not player:
        return

    action = _handle_pause_input(events)
    if action == "menu":
        return action

    #ffreeze gameplay updates while the pause overlay is open.
    if is_paused:
        return None

    #the countdown is drawn on screen, but the actual gameplay stays frozen here.
    if resume_countdown > 0:
        resume_countdown = max(0.0, resume_countdown - dt)
        return None

    #check for shooting and shoot bullets
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # mouse position in screen coordinates
            mouse_screen = pygame.Vector2(pygame.mouse.get_pos())

            # convert to world coordinates accounting for camera zoom
            mouse_world = mouse_screen / camera.zoom + camera.offset

            # player position in world coordinates
            player_pos = pygame.Vector2(player.rect.center)

            # calculate direction from player to mouse
            direction = mouse_world - player_pos
            if direction.length() != 0:
                direction = direction.normalize()

            # spawn a bullet at player center
            bullets.append(GunProjectile(*player.rect.center, direction))

    #update the bullets
    for b in bullets:
        b.update(dt)
      
    if timer:
        timer.update(events)
    player.update(dt, keys, obstacle)
    camera.update(player)

    for e in enemies:
        e.update(dt, player.rect.center)


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

    for b in bullets:
        b.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)

    obstacle.draw(screen, camera)
    if timer:
        timer.draw(screen)

    #only one pause ui state is shown at a time menu countdown or small button.
    if is_paused:
        pause_menu.draw_overlay(screen)
    elif resume_countdown > 0:
        pause_menu.draw_resume_countdown(screen, max(1, math.ceil(resume_countdown)))
    else:
        pause_menu.draw_pause_button(screen)

    pygame.display.flip()
