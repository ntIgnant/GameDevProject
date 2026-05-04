import os
import cv2
import pygame
import Game.audio as audio


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# The path for video and audio are handled separately because opencv couldn't play the video with sound, so mp4 and mp3 are handeled as two separated tracks

VIDEO_PATH = os.path.join(BASE_DIR, "Assets", "Story", "final_sequence_01.mp4") # path for mp4 vid
AUDIO_FILE = "final_sequence_01.mp3" # path for video audio track mp3


# The following are global args/objs for opencv to work (play the video)
video = None
current_frame = None
frame_time = 1 / 30 # limited to 30fps
time_since_last_frame = 0.0
finished = False

# main function to play the video and audio
def start_video():
    global video, current_frame, frame_time, time_since_last_frame, finished

    stop_video() # stop the video at first, to handle 'autoplay' bug
    current_frame = None
    time_since_last_frame = 0.0
    finished = False

    video = cv2.VideoCapture(VIDEO_PATH)
    if not video.isOpened():
        finished = True
        return False

    # Set frames per second playback
    fps = video.get(cv2.CAP_PROP_FPS)
    if fps > 0:
        frame_time = 1 / fps
    else:
        frame_time = 1 / 30

    audio.play_music(AUDIO_FILE, loops=0, volume=1.0) # play audio file (different track as video file)
    return read_next_frame()


# helper function that stops the video at the beginning (fix initial autoplay bug)
def stop_video():
    global video

    if video is not None:
        video.release()
        video = None

    audio.stop_music()

# Used in main to call 'menu' event after the video is played (this can be removed ngl)
def handle_event(event):
    return None


# This functions handles video playback for the event 'done' for main. when main receives 'done', it jumps to main menu
def update(dt):
    global time_since_last_frame

    if finished:
        return "done" # Event 'done' -> main menu (logic implemented in main.py)

    time_since_last_frame += min(dt, frame_time * 2)

    # reads video frames untill they finish, once there is no 'next frame' that means the video is over
    while time_since_last_frame >= frame_time:
        time_since_last_frame -= frame_time

        # moment where there is no more frame (video is over)
        if not read_next_frame():
            return "done" # return 'done' flag to main -> jumpt to menu

    return None

# Helper function to 'read a frame' from the video
# This is used in 'update' function, to loop it until there iss no more frame to read (video finished)
def read_next_frame():
    global current_frame, finished

    success, frame = video.read()
    if not success:
        finished = True
        stop_video()
        return False

    # This just converts a frame of the video from opencv format to pygame, to represent it using pygame
    # frame opencv format -> pygame allowed format (to show it during the pygame program execution)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.transpose(frame)
    current_frame = pygame.surfarray.make_surface(frame)
    return True

# This 'shows' each frame (correct pygame format) on the screen
def draw(screen):
    screen.fill((0, 0, 0))

    if current_frame is None:
        return

    # Here, 'screen' is the pygame program screen, not the actual monitor of the device

    # Full 'program screen' values
    # This is limited to HD (1280x720) in settings.py
    screen_width, screen_height = screen.get_size()
    frame_width, frame_height = current_frame.get_size()

    scale = min(screen_width / frame_width, screen_height / frame_height)
    new_width = int(frame_width * scale)
    new_height = int(frame_height * scale)

    scaled_frame = pygame.transform.smoothscale(current_frame, (new_width, new_height))
    x = (screen_width - new_width) // 2
    y = (screen_height - new_height) // 2
    screen.blit(scaled_frame, (x, y))
