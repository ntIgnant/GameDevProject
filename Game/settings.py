# Global configuration variables for the game

# Resolution and FPSs
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Game Progress (NEEDS TO BE CHANGED TO CONFIG FILE LATER e.g JSON FILE)
TOTAL_LEVELS = 4
# Global configuration variables for the game

# Resolution
RESOLUTIONS = {
    "HD": (1280, 720),
    "FHD": (1920, 1080)
}

CURRENT_RESOLUTION = "HD" # Default Resolution

WIDTH, HEIGHT = RESOLUTIONS[CURRENT_RESOLUTION] # Resolution aplied in game

# FPS
FPS_OPTIONS = {"30": 30, "60": 60, "120": 120}
CURRENT_FPS = "60" # Default value for the FPS
FPS = FPS_OPTIONS[CURRENT_FPS] # Value aplied in game

# Game Progress (NEEDS TO BE CHANGED TO CONFIG FILE LATER e.g JSON FILE)
TOTAL_LEVELS = 4
LEVELS_COMPLETED = [] # Initially as empty list (new game)