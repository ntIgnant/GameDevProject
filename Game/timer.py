import pygame
import Game.settings as settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets", "pause_menu")

TABLE_PATH = os.path.join(ASSETS_DIR, "Table.png")

pygame.init()

class Timer():
    def __init__(self, minutes):
        self.seconds = minutes * 60 # total seconds
        self.font = pygame.font.SysFont(None, 80)
        self.clock = pygame.time.Clock()
        self.run = True
        self.colour = (250, 250, 250) #TODO: find a better colour
        self.timer_event = pygame.USEREVENT + 1 # create an event for the timer ticks
        pygame.time.set_timer(self.timer_event, 1000) # the event happens every second (1000 milliseconds = 1 second)
        self.text = self.font.render(self.time_format(), True, self.colour)
        self.background_img = pygame.image.load(TABLE_PATH)
        self.background_img = pygame.transform.scale(self.background_img, (250, 80))
        self.background_rect = self.background_img.get_rect(center=(settings.WIDTH//2, 50))

    def time_format(self):
        # returning the countdown string using the format MM:SS
        return f"{self.seconds // 60:02}:{self.seconds % 60:02}"

    def update(self, events):
        for event in events:
            if event.type == self.timer_event:
                # decrease the number of seconds remained
                self.seconds -= 1
                if self.seconds == 0:
                    # if there are no seconds left, the timer stops + "level failed" screen logic
                    pygame.time.set_timer(self.timer_event, 0)
                    #TODO: add the logic for the "level failed" screen
                       
                self.text = self.font.render(self.time_format(), True, self.colour)        
            
    def draw(self, screen):
        screen.blit(self.background_img, self.background_rect)
        
        text_rect = self.text.get_rect(center = self.background_rect.center)
        screen.blit(self.text, text_rect)

