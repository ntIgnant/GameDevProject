import os # for mp3 files lookup
import pygame

# Base dirs for Sound FX and Music (Music to be implemented)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SOUND_FX_DIR = os.path.join(BASE_DIR, "Assets", "Audio", "Sound_FX") # Directory where the Sound FX are located
MUSIC_DIR = os.path.join(BASE_DIR, "Assets", "Audio", "Music") # Directory where the Music Is located

# Audio related settings
_mixer_ready = False
_sounds = {}
_default_volume = 0.7


def _get_mixer():
    try:
        mixer = pygame.mixer
    except (AttributeError, NotImplementedError):
        return None
    if mixer.__class__.__name__ == "MissingModule":
        return None
    return mixer


def init_audio():
    global _mixer_ready

    if _mixer_ready:
        return True

    mixer = _get_mixer()
    if mixer is None:
        _mixer_ready = False
        return False

    try:
        if not mixer.get_init():
            mixer.init()
        _mixer_ready = True
    except (pygame.error, NotImplementedError):
        _mixer_ready = False

    return _mixer_ready


def is_ready():
    mixer = _get_mixer()
    return _mixer_ready and mixer is not None and mixer.get_init() is not None


def register_sound(name, filename, volume=None):
    if not init_audio():
        return None

    path = os.path.join(SOUND_FX_DIR, filename)
    mixer = _get_mixer()
    if mixer is None:
        return None

    try:
        sound = mixer.Sound(path)
    except (pygame.error, FileNotFoundError, NotImplementedError):
        return None
    sound.set_volume(_default_volume if volume is None else volume)
    _sounds[name] = sound
    return sound


def load_sound(name, filename, volume=None):
    return register_sound(name, filename, volume)


def get_sound(name):
    return _sounds.get(name)


def play_sound(name):
    sound = get_sound(name)
    if sound is None:
        return None
    return sound.play()


def load_game_sfx():
    load_sound("alien_hit", "alien-being-hit.mp3", volume=0.55)
    load_sound("boss_damage", "boss-damage.mp3", volume=0.6)
    load_sound("game_over", "game-over.mp3", volume=0.7)
    load_sound("gun_shot", "gun-shot.mp3", volume=0.45)
    load_sound("player_hit", "player-being-damaged.mp3", volume=0.6)


def set_default_volume(volume):
    global _default_volume
    _default_volume = max(0.0, min(1.0, volume))


def set_sound_volume(name, volume):
    sound = get_sound(name)
    if sound is None:
        return
    sound.set_volume(max(0.0, min(1.0, volume)))


def stop_all_sfx():
    if not is_ready():
        return
    mixer = _get_mixer()
    if mixer is None:
        return
    mixer.stop()
