# Global configuration variables for the game

# Resolution
RESOLUTIONS = {
    "HD": (1280, 720),
    "FHD": (1920, 1080)
}

CURRENT_RESOLUTION = "HD" # Default Resolution
CURRENT_SCREEN_SIZE = RESOLUTIONS[CURRENT_RESOLUTION]
WIDTH, HEIGHT = CURRENT_SCREEN_SIZE # Resolution aplied in game

def set_resolution(name):
    global CURRENT_RESOLUTION, CURRENT_SCREEN_SIZE, WIDTH, HEIGHT

    CURRENT_RESOLUTION = name
    CURRENT_SCREEN_SIZE = RESOLUTIONS[CURRENT_RESOLUTION]
    WIDTH, HEIGHT = CURRENT_SCREEN_SIZE

# FPS
FPS_OPTIONS = {"30": 30, "60": 60, "120": 120}
CURRENT_FPS = "60" # Default value for the FPS
FPS = FPS_OPTIONS[CURRENT_FPS] # Value aplied in game

# Game Progress (NEEDS TO BE CHANGED TO CONFIG FILE LATER e.g JSON FILE)
TOTAL_LEVELS = 4
LEVELS_COMPLETED = [] # Initially as empty list (new game)
