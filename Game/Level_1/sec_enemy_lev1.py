# Logic for the 'Secondary Enemy' of the Level 1
import os
import pygame
from Game.camera import Camera

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

ENEMY_FRAME_W = 32
ENEMY_FRAME_H = 32
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

    return frames # Returns a list with the frames that form the movement animation of the enemy walking


def load_walk_frames():
    """Call after pygame display is initialized."""
    walk_path = os.path.join(ASSETS_DIR, "Characters", "Enemy", "enemy1_walk.png")
    frames = load_spritesheet(walk_path, ENEMY_FRAME_W, ENEMY_FRAME_H)
    return [
        pygame.transform.scale(f, (ENEMY_FRAME_W * SCALE, ENEMY_FRAME_H * SCALE))
        for f in frames
    ]

# Object of the Secondary Enemy of Level 1
class SecEnemyLev1:
    def __init__(self, pos, walk_frames):
        self.pos = pygame.Vector2(pos)
        self.speed = 160

        self.walk_frames = walk_frames
        self.frame_index = 0.0
        self.anim_fps = 10.0

    def update(self, dt, target_center):
        to_target = pygame.Vector2(target_center) - self.pos
        dist = to_target.length()

        if dist > 2:
            self.pos += to_target.normalize() * self.speed * dt

            if self.walk_frames:
                self.frame_index += self.anim_fps * dt
                if self.frame_index >= len(self.walk_frames):
                    self.frame_index = 0.0

    def draw(self, screen, camera):
        if not self.walk_frames:
            return
        frame = self.walk_frames[int(self.frame_index)]
        rect = frame.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        rect = camera.apply(rect)
        
        # zooming in and drawing the enemy
        zoom = pygame.transform.scale(frame, rect.size)
        screen.blit(zoom, rect.topleft)