import os
import math
import pygame
from .settings import WIDTH, HEIGHT

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

class Player:
    def __init__(self):
        self.size = 40
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, self.size, self.size)
        self.speed = 300
        #health(we can connect it to damage later)
        self.max_health = 100
        self.health = 100
        self.dash_distance = 140
        self.dash_cooldown = 5.0
        self.dash_cooldown_remaining = 0.0
        self.dash_requested = False
        self.last_move_dir = pygame.Vector2(1, 0)

        # loading walk animation (can be moved elsewhere)
        sheet = pygame.image.load(
            os.path.join(ASSETS_DIR, "Characters", "Player", "player_walk.png")
        ).convert_alpha()

        self.frames = []
        for x in range(0, sheet.get_width(), 32):
            frame = sheet.subsurface((x, 0, 32, 32))
            frame = pygame.transform.scale(frame, (64, 64))#we can adjust the scale if needed
            self.frames.append(frame)

        self.frame_index = 0
        self.timer = 0
        self.facing_right = True

        ui = pygame.image.load(
            os.path.join(ASSETS_DIR, "Characters", "Player", "Health_Sheet.png")
        ).convert_alpha()

        ui_w, ui_h = ui.get_size()

        HEART_RECT = pygame.Rect(0, 132, 40, 34)
        BG_RECT    = pygame.Rect(31, 60, 92, 13)
        FILL_RECT  = pygame.Rect(31, 100, 92, 13)

        HEART_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        BG_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
        FILL_RECT.clamp_ip(pygame.Rect(0, 0, ui_w, ui_h))
                

        
        self.heart_img = ui.subsurface(HEART_RECT).copy()
        self.bar_bg = ui.subsurface(BG_RECT).copy()
        self.bar_fill = ui.subsurface(FILL_RECT).copy()

        # Scaling down the UI elements for a more compact display above the player character
        ui_scale = 0.4 
        self.heart_img = pygame.transform.scale_by(self.heart_img, ui_scale)
        self.bar_bg = pygame.transform.scale_by(self.bar_bg, ui_scale)
        self.bar_fill = pygame.transform.scale_by(self.bar_fill, ui_scale)
        # initial health values
        self.health = 100
        self.max_health = 100
        self.display_health = 100 # This smoothly follows self.health
        


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.dash_requested = True

    def _apply_dash(self, dash_dir):
        if self.dash_cooldown_remaining > 0:
            return

        self.rect.x += int(dash_dir.x * self.dash_distance)
        self.rect.y += int(dash_dir.y * self.dash_distance)
        if dash_dir.x != 0:
            self.facing_right = dash_dir.x > 0
        self.dash_cooldown_remaining = self.dash_cooldown

    def update(self, dt, keys, obstacles):
        if self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining = max(0, self.dash_cooldown_remaining - dt)

        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]

        moving = (dx != 0 or dy != 0)
# normalising so diagonal movement isn't faster
        if moving:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.last_move_dir.update(dx, dy)

           #moving left and right logic
            self.rect.x += int(dx * self.speed * dt)
            for obstacle in obstacles.coordinates:
                if self.rect.colliderect(obstacle):
                    if dx > 0:
                        self.rect.right = obstacle.left #player moving right
                    elif dx < 0:
                        self.rect.left = obstacle.right #player moving left

           #moving up and down logic
            self.rect.y += int(dy * self.speed * dt)
            for obstacle in obstacles.coordinates:
                if self.rect.colliderect(obstacle):
                    if dy > 0:
                        self.rect.bottom = obstacle.top #moving down
                    if dy < 0:
                        self.rect.top = obstacle.bottom #moving up

            if dx != 0:
                self.facing_right = dx > 0

            self.timer += dt
            if self.timer > 0.1:
                self.timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0
            self.timer = 0

        if self.dash_requested:
            if moving:
                dash_dir = pygame.Vector2(dx, dy)
            else:
                dash_dir = self.last_move_dir.copy()
                if dash_dir.length_squared() == 0:
                    dash_dir = pygame.Vector2(1 if self.facing_right else -1, 0)
            self._apply_dash(dash_dir)
            self.dash_requested = False

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        # TEMP test: health goes down automatically
        if self.health > 0:
            self.health -= 10 * dt  # Drains 10 HP every second
         
        self.display_health += (self.health - self.display_health) * 5.0 * dt


    def draw_health_ui(self, screen, camera):
       
        #calculate the current health ratio as a value between 0 and 1 for UI display
        ratio = max(0, min(1, self.display_health / self.max_health))
        
        
        #determines the scaling factor for the heart icon, with a pulsing effect when health is low to indicate danger
       
        base_scale = 1.1
        heart_pulse = base_scale
        if ratio <= 0.25:
            # Oscillation speed: 0.02, intensity: 0.1
            heart_pulse = base_scale + 0.1 + math.sin(pygame.time.get_ticks() * 0.02) * 0.1
        
       
        # create a segmented health bar , divided into segments with gaps
        internal_w = 40 
        internal_h = 6
        bar_surf = pygame.Surface((internal_w, internal_h), pygame.SRCALPHA)
        # fill with black to create the lines between segments
        bar_surf.fill((0, 0, 0)) 
        
        num_segments = 4
        segment_gap = 1 
        seg_w = (internal_w - (segment_gap * (num_segments - 1))) // num_segments
        
        for i in range(num_segments):
            seg_x = i * (seg_w + segment_gap)
            
            # Draw Empty Segment (Grey)
            pygame.draw.rect(bar_surf, (70, 70, 70), (seg_x, 0, seg_w, internal_h))
            
            # Draw Filled Segment (Red)
            seg_start = i / num_segments
            if ratio > seg_start:
                seg_ratio = min(1, (ratio - seg_start) * num_segments)
                current_seg_w = int(seg_w * seg_ratio)
                
                if current_seg_w > 0:
                    # Base Red
                    pygame.draw.rect(bar_surf, (172, 50, 50), (seg_x, 0, current_seg_w, internal_h))
                    # Top Highlight (Pinkish)
                    pygame.draw.rect(bar_surf, (217, 87, 99), (seg_x, 0, current_seg_w, 1))
                    # Bottom Shadow (Dark Red)
                    pygame.draw.rect(bar_surf, (118, 23, 45), (seg_x, internal_h - 1, current_seg_w, 1))

        
        #calculate the base positions for the heart and bar relative to the player's position
        left_shift = 30
        gap = -1 # gap between heart and bar
        base_x = self.rect.centerx - left_shift
        base_y = self.rect.top - 22

        
        #apply camera transformation to the heart's position for proper rendering in the game
        h_cam_rect = camera.apply(pygame.Rect(base_x, base_y - 3, self.heart_img.get_width(), self.heart_img.get_height()))
        
        #calculate the pulsed size of the heart based on the current health ratio, creating a pulsing effect when health is low
        pulsed_heart_w = int(h_cam_rect.width * heart_pulse)
        pulsed_heart_h = int(h_cam_rect.height * heart_pulse)
        
        #calculate the position to draw the heart, centering it on the camera-transformed position and adjusting for the pulsing size
        heart_draw_pos = (
            h_cam_rect.centerx - pulsed_heart_w // 2,
            h_cam_rect.centery - pulsed_heart_h // 2 - 4
        )

        
        # Draw Heart Outline
        #fill the heart with black to create an outline effect, then draw the pulsed heart on top for a dynamic health indicator
        scaled_heart = pygame.transform.scale(self.heart_img, (pulsed_heart_w, pulsed_heart_h))
        outline_surf = scaled_heart.copy()
        outline_surf.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        
        thickness = 2
        for dx, dy in [(-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness)]:
            screen.blit(outline_surf, (heart_draw_pos[0] + dx, heart_draw_pos[1] + dy))

        
        # Draw the scaled heart image at the calculated position
        screen.blit(scaled_heart, heart_draw_pos)
        
        
        # Scale up the bar surface for a pixelated retro effect and position it next to the heart
        final_bar_surf = pygame.transform.scale(bar_surf, (internal_w * 2, internal_h * 2))
        bar_draw_pos = (h_cam_rect.right + gap, h_cam_rect.top + 4)
        screen.blit(final_bar_surf, bar_draw_pos)
        
        
        # Draw a black outline around the health bar
        b_rect = final_bar_surf.get_rect(topleft=bar_draw_pos)
        pygame.draw.rect(screen, (0, 0, 0), b_rect, 2)

    def draw(self, screen, camera):
        frame = self.frames[self.frame_index]
# flip when moving left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        self.draw_health_ui(screen,camera)
        # creating a new frame for the camera pov
        player_camera_frame = frame.get_rect(center = self.rect.center)
        player_camera_frame = camera.apply(player_camera_frame)

        # zooming in and drawing the player
        player_frame_zoom = pygame.transform.scale(frame, player_camera_frame.size)
        screen.blit(player_frame_zoom, player_camera_frame.topleft)
