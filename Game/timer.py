import pygame
from .settings import WIDTH, HEIGHT

pygame.init()

class Timer():
    def __init__(self, minutes):
        self.seconds = minutes * 60 # total seconds
        self.font = pygame.font.SysFont(None, 100)
        self.clock = pygame.time.Clock()
        self.run = True
        self.colour = (51, 153, 255) #TODO: find a better colour
        self.timer_event = pygame.USEREVENT + 1 # create an event for the timer ticks
        pygame.time.set_timer(self.timer_event, 1000) # the event happens every second (1000 milliseconds = 1 second)
        self.text = self.font.render(self.time_format(), True, self.colour)

    def time_format(self):
        # returning the countdown string using the format MM:SS
        return f"{self.seconds // 60:02}:{self.seconds % 60:02}"

    def add_seconds(self, seconds):
        if seconds <= 0:
            return

        self.seconds += int(seconds)
        self.text = self.font.render(self.time_format(), True, self.colour)

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
        text_rect = self.text.get_rect(center = (WIDTH // 2, 50))  
        screen.blit(self.text, text_rect)

