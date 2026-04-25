import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Extras")

PUDDLE_PATH = os.path.join(ASSETS_DIR, "lava.png")

PUDDLE_FRAME_W = 32
PUDDLE_FRAME_H = 32
SCALE = 3

# HELPER FUNCTION FOR THE 'ANIMATION' FRAMES
# It cuts the image into pieces and adds them into a list, so the list contains all the frames for the movement animation
def load_frames_puddle():
    sheet = pygame.image.load(PUDDLE_PATH).convert_alpha()
    frames = []
    sheet_width, sheet_height = sheet.get_size()

    max_x = sheet_width - PUDDLE_FRAME_W
    max_y = sheet_height - PUDDLE_FRAME_H

    for y in range(0, sheet_height, PUDDLE_FRAME_H):
        if y > max_y:
            break
        for x in range(0, sheet_width, PUDDLE_FRAME_W):
            if x > max_x:
                break
            frames.append(sheet.subsurface(pygame.Rect(x, y, PUDDLE_FRAME_W, PUDDLE_FRAME_H)))
            
    return [
        pygame.transform.scale(f, (PUDDLE_FRAME_W * SCALE, PUDDLE_FRAME_H * SCALE))
        for f in frames
    ]

class LavaPuddle:
    def __init__(self, pos, frames):
        self.damage = 15
        self.pos = pygame.Vector2(pos)
        self.pos.y += 50
        
        self.frames = frames
        self.frame_index = 0.0
        self.anim_fps = 4.0
        
        self.done = False # checks if the lava puddle disappeared
        
        # Hitbox to track if the player is over the puddle in order to make them take damage
        self.hitbox = pygame.Rect(0, 0, PUDDLE_FRAME_W * SCALE, PUDDLE_FRAME_H * SCALE)
        self.hitbox.center = (int(self.pos.x), int(self.pos.y))
        

    def update(self, dt):
        # Check if the puddle dissapeared
        if self.done:
            return
        
        self.frame_index += self.anim_fps * dt
        
        frames_count = len(self.frames)
        
        # Check if the animation for fading away finished 
        if self.frame_index >= frames_count:
            self.frame_index = frames_count -1
            self.done = True
            
    def is_done(self):
        return self.done
    
    def give_damage(self, player_rect, dt):
        # If the animation is done, the puddle does not inflict damage
        if self.done:
            return 0
        
        # If the player is over the puddle, then the player will take damage
        if self.hitbox.colliderect(player_rect):
            return self.damage * dt # The puddle gives damage continously
        
        return 0
    
    def draw(self, screen, camera):
        if self.frames is None:
            return
        
        frame = self.frames[int(self.frame_index)]
        
        rect = frame.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        rect = camera.apply(rect)
        screen.blit(frame, rect.topleft)