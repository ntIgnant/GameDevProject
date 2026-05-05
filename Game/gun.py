import pygame
import os
import math

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "Extras")

BULLET_PATH = os.path.join(ASSETS_DIR, "bullet.png")

class GunProjectile:
    bullet_img = None
    
    def __init__(self, x, y, direction):
        #self.size = 10
        if GunProjectile.bullet_img is None:
            bullet_raw= pygame.image.load(BULLET_PATH).convert_alpha()
            GunProjectile.bullet_img = pygame.transform.scale(bullet_raw, (25, 8))
        
        self.pos = pygame.Vector2(x, y)
        self.direction = direction
        self.speed = 500
        #self.color = (255, 0, 0)
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(GunProjectile.bullet_img, angle)
        self.rect = self.image.get_rect(center = (x,y))

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

    def draw(self, screen, camera):
        rect = self.image.get_rect(center = camera.apply(self.rect).center)
        #pygame.draw.rect(screen, self.color, rect)
        screen.blit(self.image, rect)
        
# For boss3, we need bullets that will follow the player (homing bullets)
# This class will handle this type of bullets
# It will be like an extentions of the original class

class HomingProjectile(GunProjectile):
    def __init__(self, x, y, direction, turn_speed = 80):
        super().__init__(x, y, direction)
        self.speed = 80 # not hard to dodge
        self.turn_speed = turn_speed
        self.target_center = None
        
    def update(self, dt):
        if self.target_center:
            target = pygame.Vector2(self.target_center) - self.pos
            
            # Turn the bullets accordingly when it follow the player
            # This makes the bullets have the correct angle and update every frame
            if target.length_squared() > 0:
                current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
                target_angle = math.degrees(math.atan2(target.y, target.x))
                
                # Get the correct difference and turn in the correct direction
                difference = (target_angle  - current_angle + 180) % 360 - 180
                
                # This helps the bullet to turn gradually rather, in a smooth way
                turn = max(-self.turn_speed *dt, min(self.turn_speed *dt, difference))
                
                # The new angle gets turned into a direction vector again
                rad = math.radians(current_angle + turn)
                self.direction = pygame.Vector2(math.cos(rad), math.sin(rad))
            
            # Update other values
            self.pos += self.direction * self.speed * dt
            self.rect.center = self.pos    