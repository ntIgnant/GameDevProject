import pygame
import os
from Game.gun import GunProjectile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

BOSS_FRAME_W = 32
BOSS_FRAME_H = 32

# These values are for the special ability warning animation
# The sprite sheet is split into 128x128 frames
FIRE_CIRCLE_FRAME_W = 128
FIRE_CIRCLE_FRAME_H = 128
SCALE = 2

# HELPER FUNCTION FOR THE 'ANIMATION' FRAMES
# It cuts the image into pieces and adds them into a list, so the list contains all the frames for the movement animation
# Each png image is a serie of frames (e.g /Assets/Characters/Enemy/enemy1_walk.png)
def load_spritesheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    sheet_width, sheet_height = sheet.get_size()

    max_x = sheet_width - frame_width
    max_y = sheet_height - frame_height

    for y in range(0, sheet_height, frame_height):
        if y > max_y:
            break
        for x in range(0, sheet_width, frame_width):
            if x > max_x:
                break
            frames.append(sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height)))

    return frames # Returns a list with the frames that form the movement animation of the boss walking


def load_walk_frames_boss():
    """Call after pygame display is initialized."""
    walk_path = os.path.join(ASSETS_DIR, "Characters", "Enemy", "boss1_walk.png")
    frames = load_spritesheet(walk_path, BOSS_FRAME_W, BOSS_FRAME_H)
    return [
        pygame.transform.scale(f, (BOSS_FRAME_W * SCALE, BOSS_FRAME_H * SCALE))
        for f in frames
    ]

def load_attack_frames_boss():
    attack_path = os.path.join(ASSETS_DIR, "Characters", "Enemy", "boss1_attack.png")
    frames = load_spritesheet(attack_path, BOSS_FRAME_W, BOSS_FRAME_H)
    return [
        pygame.transform.scale(f, (BOSS_FRAME_W * SCALE, BOSS_FRAME_H * SCALE))
        for f in frames
    ]

# This function loads the fire warning animation that appears around the boss
# before the special circle attack happens
def load_fire_circle_frames_boss():
    fire_path = os.path.join(ASSETS_DIR, "Extras", "boss_special_warning.png")
    return load_spritesheet(fire_path, FIRE_CIRCLE_FRAME_W, FIRE_CIRCLE_FRAME_H)

# Obeject of the boss of level 2
class BossLev2:
    def __init__(self, pos, walk_frames, attack_frames, fire_circle_frames=None):
        self.pos = pygame.Vector2(pos)
        self.speed = 90
        self.size = 150
        self.rect = pygame.Rect(self.pos.x - self.size // 2, self.pos.y - self.size // 2, self.size, self.size)
        
        # Health attributes for the boss
        self.max_health = 500
        self.health = 500
        self.display_health = 500.0
 
        # Class attributes for the boss position while walking/attacking
        self.walk_frames = walk_frames
        self.attack_frames = attack_frames

        #This animation is only a warning effect.It tells the player
        #that the boss special attack is about to happen"
        self.fire_circle_frames = fire_circle_frames or []
        self.fire_circle_fps = 18.0
        self.frame_index = 0.0
        self.anim_fps = 10.0
        self.anim_fps_attack = 5.0
        
        #This section controls the normal 3-bullet attack
        #Phase 2 keeps three bullets too, but shoots a bit faster
        self.state = "chase"
        self.last_attack = 0.0 # keeps track of the time that passed since the last attack
        self.attack_interval = 1.5
        self.phase_two_attack_interval = 1.1
        self.attack_windup = 0.25
        self.attack_duration = 0.50
        self.attack_fired = False

        # This section controls the special ability
        #The boss waits, shows the fire warning, then fires bullets around itself
        #In phase 2 it repeats the circle burst once more shortly after the first one
        self.special_timer = 0.0
        self.special_interval = 8.0
        self.phase_two_special_interval = 6.0
        self.special_windup = 1.4
        self.phase_two_special_repeat_delay = 0.25
        self.special_shots_fired = 0
        self.recover_duration = 0.5

        self.state_counter = 0.0 # keeps track for how long the boss was in one state

        # This section is for the boss movement
        # The boss tries to keep a good distance and strafe around the player
        self.preferred_min_distance = 220
        self.preferred_max_distance = 360
        self.strafe_direction = 1
        self.strafe_timer = 0.0
        self.strafe_switch_time = 2.0
        
        # initialy, the assets is facing right
        self.facing_right = True
        
        # This queue is used by level_2.py
        # The boss creates bullets here, then level_2.py takes them and updates/draws them
        self.bullet_queue = []
        self.bullet_speed = 330
        self.phase_two_bullet_speed = 360
        self.normal_spread_angle = 12
        self.phase_two_spread_angle = 18
        self.special_bullet_count = 12
        self.phase_two_special_bullet_count = 16
        
        # Directory to access the sec-enemy health-bar (same as the player but purple)
        healthbar_path = os.path.join(ASSETS_DIR, "Characters", "Enemy", "Healthbar_sec_enemy.png")
        ui = pygame.image.load(healthbar_path).convert_alpha()
        ui_w, ui_h = ui.get_size()

        # All the following of this function, is about the creation for the healthbar (copies the same structure as the player healthbar)
        heart_rect = pygame.Rect(0, 132, 40, 34)
        bg_rect = pygame.Rect(31, 60, 92, 13)
        fill_rect = pygame.Rect(31, 100, 92, 13)

        heart_rect.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        bg_rect.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        fill_rect.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))

        self.heart_img = ui.subsurface(heart_rect).copy()
        self.bar_bg = ui.subsurface(bg_rect).copy()
        self.bar_fill = ui.subsurface(fill_rect).copy()

        ui_scale = 0.3
        self.heart_img = pygame.transform.scale_by(self.heart_img, ui_scale)
        self.bar_bg = pygame.transform.scale_by(self.bar_bg, ui_scale)
        self.bar_fill = pygame.transform.scale_by(self.bar_fill, ui_scale)

    # This function updates the current health of the sec-enemy (fur bullet damage)
    # the 'amount' parameter is a 'damage' value that can be modified in level_2.py (damage of the bullet)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    # This function just checks if the health of the enemy is > 0
    # This is ued in level_2.py to evaluate if enemy should still appear or not in the map
    def is_alive(self):
        return self.health > 0

    def _clamp_to_area(self, area_rect):
        if area_rect is None:
            return
        self.rect.clamp_ip(area_rect)
        self.pos.update(self.rect.centerx, self.rect.centery)

    # This function checks if the boss has reached phase 2
    # Phase 2 starts when the boss is at half health or lower
    def _is_phase_two(self):
        return self.health <= self.max_health / 2

    #This function creates one boss bullet
    #It also gives phase 2 bullets their stronger fire/glow look
    def _make_bullet(self, direction):
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()
        spawn_pos = self.pos + direction * (self.size // 2 - 10)
        bullet = GunProjectile(spawn_pos.x, spawn_pos.y, direction)
        phase_two = self._is_phase_two()
        bullet.speed = self.phase_two_bullet_speed if phase_two else self.bullet_speed
        bullet.ignore_obstacles = False

        #Ths recolors the normal bullet into a fire bulet
        bullet.image = bullet.image.copy()
        bullet.image.fill((255, 115, 35, 255), special_flags=pygame.BLEND_RGBA_MULT)
        bullet.image.fill((90, 25, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        if phase_two:
        #Phase 2 bullets get a small glow so they look more dangerous
        #but they still collide with obstacles like normal bullets
            center = bullet.rect.center
            glow = pygame.Surface((bullet.image.get_width() + 14, bullet.image.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 70, 0, 80), glow.get_rect())
            pygame.draw.ellipse(glow, (255, 210, 70, 120), glow.get_rect().inflate(-8, -8))
            glow.blit(bullet.image, (7, 7))
            bullet.image = glow
            bullet.rect = bullet.image.get_rect(center=center)
        bullet.rect = bullet.image.get_rect(center=bullet.rect.center)
        self.bullet_queue.append(bullet)

    # This function fires the boss normal attack
    # It shoots three bullets: left angle, middle, and right angle
    def _shoot_spread(self, target_center):
        direction = pygame.Vector2(target_center) - self.pos
        if direction.length_squared() == 0:
            return

        spread = self.phase_two_spread_angle if self._is_phase_two() else self.normal_spread_angle
        for angle in (-spread, 0, spread):
            self._make_bullet(direction.rotate(angle))

    # This function fires the special ability circle attack
    # The angle_offset lets phase 2 fire the second circle slightly rotated
    def _shoot_special(self, angle_offset=0):
        bullet_count = self.phase_two_special_bullet_count if self._is_phase_two() else self.special_bullet_count
        for index in range(bullet_count):
            angle = 360 / bullet_count * index + angle_offset
            self._make_bullet(pygame.Vector2(1, 0).rotate(angle))

    #This function moves the boss while keeping it inside the level and away from the player
    #The boss ignores obstacles on purpose, because it is large and got stuck on small objects
    def _move_with_collisions(self, movement, obstacles, player_rect, area_rect):
        if movement.length_squared() == 0:
            return False

        collision_x = False
        self.pos.x += movement.x
        self.rect.centerx = int(self.pos.x)

        if player_rect is not None and self.rect.colliderect(player_rect):
            collision_x = True
            if movement.x > 0:
                self.rect.right = player_rect.left
            elif movement.x < 0:
                self.rect.left = player_rect.right
            self.pos.x = self.rect.centerx

        self._clamp_to_area(area_rect)

        collision_y = False
        self.pos.y += movement.y
        self.rect.centery = int(self.pos.y)

        if player_rect is not None and self.rect.colliderect(player_rect):
            collision_y = True
            if movement.y > 0:
                self.rect.bottom = player_rect.top
            elif movement.y < 0:
                self.rect.top = player_rect.bottom
            self.pos.y = self.rect.centery

        self._clamp_to_area(area_rect)
        return collision_x or collision_y

    def update(self, dt, target_center, obstacles, player_rect=None, area_rect=None, speed_multiplier=1.0):
        to_target = pygame.Vector2(target_center) - self.pos
        dist = to_target.length()
        speed_scale = max(0.0, speed_multiplier)

        if abs(to_target.x) > 1:
            self.facing_right = to_target.x > 0
        
        if self.state == "attack":
            #This state is the short pause before the normal 3-bullet shot
            #The pause makes the attack feel less instant and more readable
            self.state_counter += dt
            if self.attack_frames:
                self.frame_index += self.anim_fps_attack * dt
                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0.0

            if not self.attack_fired and self.state_counter >= self.attack_windup:
                self._shoot_spread(target_center)
                self.attack_fired = True

            if self.state_counter >= self.attack_duration:
                self.state = "chase"
                self.state_counter = 0.0
                self.frame_index = 0.0

            self.display_health += (self.health - self.display_health) * 5.0 * dt
            return

        if self.state == "special":
            # This state is the boss special ability
            # The warning animation plays first, then the circle bullets are fired
            self.state_counter += dt
            if self.attack_frames:
                self.frame_index += self.anim_fps_attack * dt
                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0.0

            if self._is_phase_two():
                # Phase 2 special is stronger: it fires one circle
                #waits a tiny moment then fires a second rotated circle
                if self.special_shots_fired == 0 and self.state_counter >= self.special_windup:
                    self._shoot_special()
                    self.special_shots_fired = 1

                if self.special_shots_fired == 1 and self.state_counter >= self.special_windup + self.phase_two_special_repeat_delay:
                    second_burst_offset = 360 / self.phase_two_special_bullet_count / 2
                    self._shoot_special(second_burst_offset)
                    self.state = "recover"
                    self.state_counter = 0.0
                    self.frame_index = 0.0
            elif self.state_counter >= self.special_windup:
                self._shoot_special()
                self.state = "recover"
                self.state_counter = 0.0
                self.frame_index = 0.0

            self.display_health += (self.health - self.display_health) * 5.0 * dt
            return

        if self.state == "recover":
            # After attackingthe boss pauses for a moment before moving again
            self.state_counter += dt
            if self.state_counter >= self.recover_duration:
                self.state = "chase"
                self.state_counter = 0.0
            self.display_health += (self.health - self.display_health) * 5.0 * dt
            return

        self.last_attack += dt
        self.special_timer += dt

        current_attack_interval = self.phase_two_attack_interval if self._is_phase_two() else self.attack_interval
        current_special_interval = self.phase_two_special_interval if self._is_phase_two() else self.special_interval

        if self.special_timer >= current_special_interval:
            # This starts the special ability and resets the counters used by it
            self.state = "special"
            self.special_timer = 0.0
            self.special_shots_fired = 0
            self.state_counter = 0.0
            self.frame_index = 0.0
            return

        if self.last_attack >= current_attack_interval:
            # This starts the normal 3-bullet attack
            self.state = "attack"
            self.last_attack = 0.0
            self.attack_fired = False
            self.state_counter = 0.0
            self.frame_index = 0.0
            return

        if dist > 2 and self.state == "chase":
            #This section is the normal movement
            #Far away: move closer. Too close: back away
            self.strafe_timer += dt
            if self.strafe_timer >= self.strafe_switch_time:
                self.strafe_timer = 0.0
                self.strafe_direction *= -1

            target_dir = to_target.normalize()
            if dist > self.preferred_max_distance:
                movement_dir = target_dir
            elif dist < self.preferred_min_distance:
                movement_dir = -target_dir
            else:
                movement_dir = pygame.Vector2(-target_dir.y, target_dir.x) * self.strafe_direction

            current_speed = self.speed * (1.15 if self._is_phase_two() else 1.0)
            movement = movement_dir.normalize() * current_speed * speed_scale * dt
            if self._move_with_collisions(movement, obstacles, player_rect, area_rect):
                self.strafe_direction *= -1

            if self.walk_frames:
                self.frame_index += self.anim_fps * dt * speed_scale
                if self.frame_index >= len(self.walk_frames):
                    self.frame_index = 0.0

        self.display_health += (self.health - self.display_health) * 5.0 * dt
    
    #This functions puts the healthbar of the sec-enemy above this one
    #The following code is preatty much the same as the healthbar draw for the player
    def draw_health_ui(self, screen, camera):
        ratio = max(0, min(1, self.display_health / self.max_health))
        internal_w = 40
        internal_h = 6
        bar_surf = pygame.Surface((internal_w, internal_h), pygame.SRCALPHA)
        bar_surf.fill((0, 0, 0))

        num_segments = 4
        segment_gap = 1
        seg_w = (internal_w - (segment_gap * (num_segments - 1))) // num_segments

        for i in range(num_segments):
            seg_x = i * (seg_w + segment_gap)
            pygame.draw.rect(bar_surf, (70, 70, 70), (seg_x, 0, seg_w, internal_h))

            seg_start = i / num_segments
            if ratio > seg_start:
                seg_ratio = min(1, (ratio - seg_start) * num_segments)
                current_seg_w = int(seg_w * seg_ratio)
                if current_seg_w > 0:
                    pygame.draw.rect(bar_surf, (178, 73, 255), (seg_x, 0, current_seg_w, internal_h))
                    pygame.draw.rect(bar_surf, (220, 164, 255), (seg_x, 0, current_seg_w, 1))
                    pygame.draw.rect(bar_surf, (95, 34, 145), (seg_x, internal_h - 1, current_seg_w, 1))

        # Change this values to change the healthbar dimensions
        bar_world_rect = pygame.Rect(
            self.rect.centerx - 40,
            self.rect.top - 16,
            40,
            6,
        )
        bar_cam_rect = camera.apply(bar_world_rect)
        final_bar_surf = pygame.transform.scale(bar_surf, (internal_w * 2, internal_h * 2))
        bar_draw_pos = (
            bar_cam_rect.centerx - final_bar_surf.get_width() // 2,
            bar_cam_rect.y,
        )
        screen.blit(final_bar_surf, bar_draw_pos)

        bar_rect = final_bar_surf.get_rect(topleft=bar_draw_pos)
        pygame.draw.rect(screen, (0, 0, 0), bar_rect, 2)

    def draw_special_warning(self, screen, camera):
        if self.state != "special":
            return

        # This draws the animated fire warning around the boss
        # It grows a little during the windup so the player can read the danger
        progress = min(1.0, self.state_counter / self.special_windup)
        warning_size = int(self.size * (1.25 + progress * 0.12))
        warning_rect = pygame.Rect(0, 0, warning_size, warning_size)
        warning_rect.center = (int(self.pos.x), int(self.pos.y))
        camera_rect = camera.apply(warning_rect)

        if self.fire_circle_frames:
            # This uses the PNG sprite sheet from Assets/Extras/boss_special_warning.png
            frame_index = int(self.state_counter * self.fire_circle_fps) % len(self.fire_circle_frames)
            frame = pygame.transform.scale(self.fire_circle_frames[frame_index], camera_rect.size)
            screen.blit(frame, camera_rect.topleft)
            return

       


    def draw(self, screen, camera):
        if not self.walk_frames:
            return

        self.draw_health_ui(screen, camera)
        
        if self.state in ("attack", "special") and self.attack_frames:
            frame = self.attack_frames[int(self.frame_index) % len(self.attack_frames)]
        else:
            frame = self.walk_frames[int(self.frame_index) % len(self.walk_frames)]
        
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            
        # Resize the boss assets accordingly to its size
        scaled_boss = pygame.transform.scale(frame, (self.size, self.size))
        
        rect = scaled_boss.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        rect = camera.apply(rect)
        
        # zooming in and drawing the boss
        zoom = pygame.transform.scale(frame, rect.size)
        screen.blit(zoom, rect.topleft)
        self.draw_special_warning(screen, camera)
