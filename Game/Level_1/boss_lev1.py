import pygame
import os
from Game.camera import Camera

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

BOSS_FRAME_W = 32
BOSS_FRAME_H = 32
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

# Obeject of the boss of level 1
class BossLev1:
    def __init__(self, pos, walk_frames, attack_frames):
        self.pos = pygame.Vector2(pos)
        self.speed = 90
        self.size = 150
        self.rect = pygame.Rect(self.pos.x - self.size // 2, self.pos.y - self.size // 2, self.size, self.size)
        
        # Health attributes for the boss
        self.max_health = 200
        self.health = 200
        self.display_health = 200.0
 
        # Class attributes for the boss position while walking/attacking
        self.walk_frames = walk_frames
        self.attack_frames = attack_frames
        self.frame_index = 0.0
        self.anim_fps = 10.0
        self.anim_fps_attack = 5.0
        
        # The boss will attack every few seconds (4 in this case)
        self.state = "idle"
        self.last_attack = 0.0 # keeps track of the time that passed since the last attack
        self.attack_interval = 4.0
        
        
        self.chasing = 3.0 # for how long the boss follows the player
        self.idle = 2.0 # for how long the boss stays still
        self.state_counter = 0.0 # keeps track for how long the boss was in one state
        
        # initialy, the assets is facing right
        self.facing_right = True
        
        # queue used to handle the puddle spawn logic while the attack animations plays
        self.puddle_queue = []
        
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
    # the 'amount' parameter is a 'damage' value that can be modified in level_1.py (damage of the bullet)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    # This function just checks if the health of the enemy is > 0
    # This is ued in level_1.py to evaluate if enemy should still appear or not in the map
    def is_alive(self):
        return self.health > 0

    def _clamp_to_area(self, area_rect):
        if area_rect is None:
            return
        self.rect.clamp_ip(area_rect)
        self.pos.update(self.rect.centerx, self.rect.centery)

    def update(self, dt, target_center, obstacles, player_rect=None, area_rect=None):
        to_target = pygame.Vector2(target_center) - self.pos
        dist = to_target.length()
        
        # Attack timer to keep track of the time since the last attack
        self.last_attack += dt
        
        # Check if enough time passed since the last attack and perform the action if yes
        if self.last_attack >= self.attack_interval and self.state != "attack":
            self.state = "attack"
            self.last_attack = 0.0 # Reset the timer
            self.frame_index = 0.0
            self.puddle_queue.append(pygame.Vector2(target_center)) # Spawn the lava puddle under the target
            
        # Animation for attack + changing the state once it's done
        if self.state == "attack":
            if self.attack_frames:
                self.frame_index += self.anim_fps_attack * dt
                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0.0
                    self.state = "idle"
                    self.state_counter = 0.0
            self.display_health += (self.health - self.display_health) * 5.0 * dt
            return
        
        self.state_counter += dt
        
        # If statements to make the boss switch between its states
        # The idle and chase statements make the boss not track the player countinously
        if self.state == "idle" and self.state_counter >= self.idle:
            self.state = "chase"
            self.state_counter = 0.0
            self.frame_index = 0.0
            
        if self.state == "chase" and self.state_counter >= self.chasing:
            self.state = "idle"
            self.state_counter = 0.0
            self.frame_index = 0.0

        if dist > 2 and self.state == "chase":
            movement = to_target.normalize() * self.speed * dt

            # The asset of the enemy should face the same as the direction it is walking to

            # Set the asset to be facing at the right
            if movement.x < 0.01:
                self.facing_right = True

            # Set the asset to be facing at the left
            elif movement.x > -0.01:
                self.facing_right = False

            # Logic for X AXIS
            collision_x = False
            self.pos.x += movement.x
            self.rect.centerx = int(self.pos.x)
            for obstacle in obstacles.collision_rects:
                if self.rect.colliderect(obstacle):
                    collision_x = True
                    if movement.x > 0:
                        self.rect.right = obstacle.left
                    elif movement.x < 0:
                        self.rect.left = obstacle.right
                    self.pos.x = self.rect.centerx

            # This part of logic checks for collision with the player
            # If the enemy collides with the player, the position should remain (for X axis)
            if player_rect is not None and self.rect.colliderect(player_rect):
                collision_x = True
                if movement.x > 0:
                    self.rect.right = player_rect.left
                elif movement.x < 0:
                    self.rect.left = player_rect.right
                self.pos.x = self.rect.centerx

            self._clamp_to_area(area_rect)

            # Logic for Y AXIS
            collision_y = False
            self.pos.y += movement.y
            self.rect.centery = int(self.pos.y)
            for obstacle in obstacles.collision_rects:
                if self.rect.colliderect(obstacle):
                    collision_y = True
                    if movement.y > 0:
                        self.rect.bottom = obstacle.top
                    elif movement.y < 0:
                        self.rect.top = obstacle.bottom
                    self.pos.y = self.rect.centery


            # This part of logic checks for collision with the player
            # If the enemy collides with the player, the position should remain (for Y axis)
            if player_rect is not None and self.rect.colliderect(player_rect):
                collision_y = True
                if movement.y > 0:
                    self.rect.bottom = player_rect.top
                elif movement.y < 0:
                    self.rect.top = player_rect.bottom
                self.pos.y = self.rect.centery


            self._clamp_to_area(area_rect)

            if collision_x or collision_y:
                movement = movement.rotate(45)

            # Animation for walking/chasing
            if self.walk_frames:
                self.frame_index += self.anim_fps * dt
                if self.frame_index >= len(self.walk_frames):
                    self.frame_index = 0.0

        self.display_health += (self.health - self.display_health) * 5.0 * dt
    
    # This functions puts the healthbar of the sec-enemy above this one
    # The following code is preatty much the same as the healthbar draw for the player
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


    def draw(self, screen, camera):
        if not self.walk_frames:
            return

        self.draw_health_ui(screen, camera)
        
        if self.state == "attack":
            frame = self.attack_frames[int(self.frame_index)]
        else:
            frame = self.walk_frames[int(self.frame_index)]    
        
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            
        # Resize the boss assets accordingly to its size
        scaled_boss = pygame.transform.scale(frame, (self.size, self.size))
        
        rect = scaled_boss.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        rect = camera.apply(rect)
        
        # zooming in and drawing the boss
        zoom = pygame.transform.scale(frame, rect.size)
        screen.blit(zoom, rect.topleft)
