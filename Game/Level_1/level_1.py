# Controller of Logic for Level 1
import math
import os
import random
import pygame
import Game.settings as settings
from Game.player import Player
from Game.gun import GunProjectile
from .sec_enemy_lev1 import SecEnemyLev1, load_walk_frames, load_attack_frames
from .boss_lev1 import BossLev1, load_walk_frames_boss, load_attack_frames_boss
from Game.obstacles import Obstacles
from Game.puddle import load_frames_puddle, LavaPuddle
from Game.timer import Timer
from Game.camera import Camera
import Game.pause_menu as pause_menu
import Game.audio as audio
from Game.upgrades import Upgrades

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

# Takes the same value set in settings
# True/False for DEV_MODE (explanation in settings.py)
DEV_MODE = settings.GLOBAL_DEV_MODE

background = None
player = None
upgrades_spawn = []
obstacle = None
enemies = []
boss = None
puddles = []
bullets = []
walk_frames = []
attack_frames = []
walk_frames_boss = []
attack_frames_boss = []
puddle_frames = []
timer = Timer(minutes = 2)
camera = Camera()
debug_font = None
CORNER_DEBUG_COLOR = (220, 70, 70, 153) # For development only, to bisualize the restricted areas of the level
is_paused = False
resume_countdown = 0.0
fire_rate = 5
fire_timer = 0
shoot_cooldown = 1 / fire_rate
exit_transition_active = False
exit_transition_fading = False
exit_transition_alpha = 0
exit_transition_target = pygame.Vector2()
EXIT_WALK_SPEED = 250
EXIT_FADE_SPEED = 170


# This is the 'damange rate' of the enemy to the player
# Lower = Faster damage
contact_damage_cooldown = 1.02
contact_damage_timer = 1.0

# 'damage rate' of one player's bullet. Used to damange enemy
# Higher number -> more damange
bullet_damage = 10

# The bullets will appear from the end of the gun
gun_offset = 25

# Variable that defines how many seconadry enemies are going to spawn (4 as default, maybe 6 to make it harder?)
BASE_SEC_ENEMY_COUNT = 4

# Partial logic for DEVMODE flag in settings
# if GLOBAL_DEV_MODE is true, show all the restricted areas AND set sec_enemies of all the levels to 0
SEC_ENEMY_COUNT = 0 if settings.GLOBAL_DEV_MODE else BASE_SEC_ENEMY_COUNT

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

# This function generates the seconary enemies in random possitions (avoiding restricted areas)
def spawn_secondary_enemies(count, area_rect, obstacles, walk_frames, attack_frames, player_rect=None):
    spawned_enemies = []
    enemy_size = 30
    padding = 12 # This value adds a 'gap/padding' between the random place where the enemies are generated, for them not to be too close
    max_attempts = max(40, count * 50)
    blockers = list(obstacles.collision_rects) # list of restricted areas (enemies cannot spawn here)
    if player_rect is not None:
        blockers.append(player_rect.inflate(160, 160))

    # Coordinates for the allowed areas where the enemies can spawn
    min_x = area_rect.left + enemy_size // 2
    max_x = area_rect.right - enemy_size // 2
    min_y = area_rect.top + enemy_size // 2
    max_y = area_rect.bottom - enemy_size // 2

    for _ in range(max_attempts):
        if len(spawned_enemies) >= count:
            break
        
        # generate two random coordinates to place the enemy (from the ranges of before)
        spawn_pos = (
            random.randint(min_x, max_x),
            random.randint(min_y, max_y),
        )
        candidate_rect = pygame.Rect(0, 0, enemy_size, enemy_size)
        candidate_rect.center = spawn_pos
        candidate_rect.inflate_ip(padding * 2, padding * 2)

        if any(candidate_rect.colliderect(blocker) for blocker in blockers):
            continue

        if any(candidate_rect.colliderect(enemy.rect.inflate(padding * 2, padding * 2)) for enemy in spawned_enemies):
            continue

        spawned_enemies.append(SecEnemyLev1(spawn_pos, walk_frames, attack_frames))

    return spawned_enemies

# This function generates the boss in a random possition (avoiding restricted areas)
def spawn_boss(area_rect, obstacles, walk_frames_boss, attack_frames_boss, player_rect=None):
    boss_size = 150
    padding = 12 # This value adds a 'gap/padding' between the random place where the boss are generated, for them not to be too close
    max_attempts = 200
    blockers = list(obstacles.collision_rects) # list of restricted areas (the boss cannot spawn here)
    if player_rect is not None:
        blockers.append(player_rect.inflate(160, 160))

    # Coordinates for the allowed areas where the boss can spawn
    min_x = area_rect.left + boss_size // 2
    max_x = area_rect.right - boss_size // 2
    min_y = area_rect.top + boss_size // 2
    max_y = area_rect.bottom - boss_size // 2

    for _ in range(max_attempts):
        # generate two random coordinates to place the boss (from the ranges of before)
        spawn_pos = (
            random.randint(min_x, max_x),
            random.randint(min_y, max_y),
        )
        candidate_rect = pygame.Rect(0, 0, boss_size, boss_size)
        candidate_rect.center = spawn_pos
        candidate_rect.inflate_ip(padding * 2, padding * 2)

        if any(candidate_rect.colliderect(blocker) for blocker in blockers):
            continue

        return BossLev1(spawn_pos, walk_frames_boss, attack_frames_boss)

    return None


# This function basically generates 'different' chasing points instead of just one unique point for the enemies to chase
# Before, the enemies were chasing a unique point (center of the player) and they were too predictable
# The function sets a chasing point for an individial enemy, based on the center of the player but applying some math to make it more 'offset'
# The radius and collapse_distance args can be changed to have different chasing points results
def get_enemy_target_point(player_center, enemy_pos, enemy_index, enemy_count, radius=70, collapse_distance=95):
    if enemy_count <= 0:
        return player_center

    if pygame.Vector2(player_center).distance_to(enemy_pos) <= collapse_distance:
        return player_center

    angle = (2 * math.pi * enemy_index) / enemy_count
    return (
        player_center[0] + math.cos(angle) * radius,
        player_center[1] + math.sin(angle) * radius,
    )

# Load Resources to initialize the level (background, ... structures should go here as well)
def load_assets():
    """Call after pygame display is initialized."""
    global background, walk_frames, attack_frames, debug_font, walk_frames_boss, attack_frames_boss, puddle_frames

    raw_background = pygame.image.load(BACKGROUND_PATH).convert()
    background = pygame.transform.smoothscale(raw_background, BASE_LEVEL_SIZE)

    walk_frames = load_walk_frames()
    attack_frames = load_attack_frames()
    walk_frames_boss = load_walk_frames_boss()
    attack_frames_boss = load_attack_frames_boss()
    puddle_frames = load_frames_puddle()
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
    global player, enemies, obstacle, bullets, is_paused, resume_countdown, contact_damage_timer, timer, puddles, boss, upgrades_spawn
    global exit_transition_active, exit_transition_fading, exit_transition_alpha

    rebuild_level_area()
    player = Player(LEVEL_AREA.center)
    bullets = []
    puddles = []
    upgrades_spawn = []
    boss = None
    obstacle = Obstacles()
    obstacle.set_corner_blockers(build_corner_object_rects())
    obstacle.spawn(area_rect=LEVEL_AREA)
    enemies = spawn_secondary_enemies(
        SEC_ENEMY_COUNT,
        LEVEL_AREA,
        obstacle,
        walk_frames,
        attack_frames,
        player.rect,
    )
    is_paused = False
    resume_countdown = 0.0
    exit_transition_active = False
    exit_transition_fading = False
    exit_transition_alpha = 0
    contact_damage_timer = 0.0
    timer.minutes = 2
    timer.seconds = 120
    timer.text = timer.font.render(timer.time_format(), True, timer.colour)
    pygame.time.set_timer(timer.timer_event, 1000)


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

def start_exit_transition():
    global exit_transition_active, exit_transition_fading, exit_transition_alpha

    exit_transition_active = True
    exit_transition_fading = False
    exit_transition_alpha = 0
    exit_transition_target.update(LEVEL_AREA.centerx, LEVEL_AREA.top + player.rect.height // 2)
    player.dashing = False

def update_exit_transition(dt):
    global exit_transition_fading, exit_transition_alpha

    if not exit_transition_fading:
        current = pygame.Vector2(player.rect.center)
        to_target = exit_transition_target - current

        if to_target.length() > 3:
            movement = to_target.normalize() * EXIT_WALK_SPEED * dt
            if movement.length() > to_target.length():
                movement = to_target

            player.rect.center = (round(current.x + movement.x), round(current.y + movement.y))
            if abs(movement.x) > 0.1:
                player.facing_right = movement.x > 0

            player.timer += dt
            if player.timer > 0.14:
                player.timer = 0
                player.frame_index = (player.frame_index + 1) % len(player.frames)
        else:
            player.rect.center = (round(exit_transition_target.x), round(exit_transition_target.y))
            player.frame_index = 0
            exit_transition_fading = True
    else:
        exit_transition_alpha = min(255, exit_transition_alpha + EXIT_FADE_SPEED * dt)
        if exit_transition_alpha >= 255:
            return "level_complete"

    camera.update(player)
    return None

def draw_exit_transition(screen):
    if not exit_transition_active or exit_transition_alpha <= 0:
        return

    fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    fade.fill((0, 0, 0, int(exit_transition_alpha)))
    screen.blit(fade, (0, 0))

# Function to update the 'state' of the match after every movement
def update_level(dt, keys, events):
    global bullets, enemies, resume_countdown, contact_damage_timer, timer, boss, fire_timer

    fire_timer -= dt

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

    if exit_transition_active:
        return update_exit_transition(dt)

    # The player's asset will be flipped based on the direction of the mouse
    # So, the player always faces the correct direction when shooting
    if player:
        mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
        mouse_world = mouse_screen / camera.zoom + camera.offset
        player_pos = pygame.Vector2(player.rect.center)
        player.facing_right = mouse_world.x > player_pos.x

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if fire_timer <= 0 :
                mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
                mouse_world = mouse_screen / camera.zoom + camera.offset
                player_pos = pygame.Vector2(player.rect.center)
                direction = mouse_world - player_pos

                if direction.length_squared() > 0:
                    normalised_direction = direction.normalize()
                    bullets.append(
                        GunProjectile(player.rect.centerx + normalised_direction.x * gun_offset,player.rect.centery + normalised_direction.y * gun_offset, normalised_direction)
                    )
                    audio.play_sound("gun_shot")

                    fire_timer = shoot_cooldown

    # Logic for bullet collision with sec-enemy (based on restricted areas)
    # If the bullet overlaps a restricted area 'e.g enemy area/off map ', then they disapear
    active_bullets = []
    for bullet in bullets:
        bullet.update(dt)
        if not LEVEL_AREA.colliderect(bullet.rect):
            continue
        
        #Shots should stop at walls and obstacles instead of passing through cover
        if any(bullet.rect.colliderect(rect) for rect in obstacle.collision_rects):
            continue

        # Check for collision between bullet and enemy, if there is collision, sec-enemy takes damange (value defined at bullet_damange)
        hit_enemy = False
        for enemy in enemies:
            if bullet.rect.colliderect(enemy.rect):
                enemy.take_damage(bullet_damage) # Update enemy health (take damange)
                audio.play_sound("alien_hit")
                hit_enemy = True
                break

        if hit_enemy:
            continue

        active_bullets.append(bullet)
    bullets = active_bullets

    timer.update(events)
    
    # Add the boss to the list of blockers so the player cannot push it
    enemy_rects = [enemy.rect for enemy in enemies]
    if boss is not None:
        # Make the rect of the boss smaller
        enemy_rects.append(boss.rect.inflate(-60,-30))
    
    player.update(dt, keys, obstacle, upgrades_spawn, enemy_rects, LEVEL_AREA)
    camera.update(player)


    # Pull one multiplier from the player so freeze can slow every enemy here
    enemy_speed_multiplier = player.get_enemy_speed_multiplier()

    if contact_damage_timer > 0:
        contact_damage_timer = max(0.0, contact_damage_timer - dt)

    # this gives each of the seconadry enemies an index to have its own 'identity'
    # for area overlapping avoidance logic and other stuff, so it treats each sec-enemy
    # instance as a different 'indexed' object
    for index, e in enumerate(enemies):
        other_enemy_rects = [enemy.rect for enemy in enemies if enemy is not e]
        target_point = get_enemy_target_point(player.rect.center, e.pos, index, len(enemies))
        e.update(dt, target_point, obstacle, player.rect, LEVEL_AREA, other_enemy_rects, enemy_speed_multiplier)

    #Spawn upgrades on dead enemy poss, takes the dead enemy then takes its position 
    dead_enemies = [enemy for enemy in enemies if not enemy.is_alive()]
    for enemy in dead_enemies:
        upgrades_spawn.append(Upgrades(enemy.pos.x, enemy.pos.y))

    # If enemy health <= 0, enemy is dead and will disapear (restricted areas will be ignored)
    enemies = [enemy for enemy in enemies if enemy.is_alive()]
    
    # If all the secondary enemies are defeated, spawn the boss
    if boss is None and not enemies:
        boss = spawn_boss(LEVEL_AREA, obstacle, walk_frames_boss, attack_frames_boss, player.rect)
        if boss:
            audio.play_music("boss-intro.mp3")
        
    if boss:
        boss.update(
            dt,
            player.rect.center,
            obstacle,
            player_rect=player.rect,
            area_rect=LEVEL_AREA,
            speed_multiplier=enemy_speed_multiplier,
        )
        
        # Spawn the puddle
        while boss.puddle_queue:
            boss.puddle_queue.pop()
            
            # Offsets to make the lava puddle be centered at the player's feet based on the direction they face
            if player.facing_right:
                puddle_x = player.rect.centerx + 20
            else:
                puddle_x = player.rect.centerx + 35
                
            puddle_y = player.rect.centery
            
            puddles.append(LavaPuddle((puddle_x, puddle_y), puddle_frames))
            
        for puddle in puddles:
            puddle.update(dt)
            damage = puddle.give_damage(player.rect, dt)
            
            if damage:
                player.take_damage(damage)
                
        for puddle in puddles[:]:
            if puddle.is_done():
                puddles.remove(puddle)
        
        # Logic for bullet collision witht the boss (based on restricted areas)
        # If the bullet overlaps a restricted area 'e.g boss area/off map ', then they disapear
        active_bullets = []
        for bullet in bullets:
            bullet.update(dt)
            if not LEVEL_AREA.colliderect(bullet.rect):
                continue

            # Check for collision between bullet and boss, if there is collision, the boss takes damange (value defined at bullet_damange)
            hit_enemy = False
            if bullet.rect.colliderect(boss.rect):
                boss.take_damage(bullet_damage) # Update boss health (take damange)
                hit_enemy = True
                break

            if hit_enemy:
                continue

            active_bullets.append(bullet)
        bullets = active_bullets
        
        if not boss.is_alive():
            audio.play_sound("success")
            audio.ensure_music("in-game.mp3")
            boss = None
            start_exit_transition()
            return None
        
    
    enemy_touching_player = any(rects_touch_or_overlap(enemy.rect, player.rect) for enemy in enemies)
    if enemy_touching_player and contact_damage_timer <= 0:
        player.take_damage(10)
        contact_damage_timer = contact_damage_cooldown

    for enemy in enemies:
        # If the player is close to the enemy, the state is switched and the enemy will attack 
        if rects_touch_or_overlap(enemy.rect, player.rect):
            current_state = "attack"
        else:
            current_state = "walk"
            
        if current_state != enemy.state:
            enemy.state = current_state
            enemy.frame_index = 0.0

    # When the player health reaches 0 or when the time is up, "game_over" flag is returned
    # This would trigger the 'Game Over Screen' in the main.py which works as the orchestrator
    if player.health <= 0 or timer.seconds <= 0:
        audio.ensure_music("in-game.mp3")
        return "game_over"

def draw_level(screen):
    if background is None:
        return

    background_camera_frame = background.get_rect(topleft=(0,0))
    background_camera_frame = camera.apply(background_camera_frame)

    # zooming in and drawing the background
    background_frame_zoom = pygame.transform.scale(background, background_camera_frame.size)
    screen.blit(background_frame_zoom, background_camera_frame.topleft)

    for puddle in puddles:
        puddle.draw(screen, camera)

    if player:
        player.draw(screen, camera)

    for bullet in bullets:
        bullet.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)
        
    if boss:
        boss.draw(screen, camera)

    for u in upgrades_spawn:
        u.draw(screen, camera)


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
    draw_exit_transition(screen)
    

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
