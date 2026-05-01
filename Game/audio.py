import os # for mp3 files lookup
import pygame

# Base dirs for Sound FX and Music
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SOUND_FX_DIR = os.path.join(BASE_DIR, "Assets", "Audio", "Sound_FX") # Directory where the Sound FX are located
MUSIC_DIR = os.path.join(BASE_DIR, "Assets", "Audio", "Music") # Directory where the Music Is located

# Audio related settings
_mixer_ready = False
_sounds = {}
music_volume = 1.0
sfx_volume = 1.0
music_muted = False
sfx_muted = False
master_muted = False
_current_music = None
_current_music_base_volume = None

# default volume levels for each sfx
SOUND_VOLUMES = {
    "alien_hit": 0.30,
    "boss_damage": 0.35,
    "boss_roar": 0.45,
    "button_click": 0.45,
    "dash": 0.35,
    "freeze": 0.40,
    "game_over": 0.70,
    "gun_shot": 0.30,
    "item_pickup": 0.35,
    "player_hit": 0.30,
    "success": 0.45,
}
 # default volum levels for music
MUSIC_VOLUMES = {
    "main-menu-sound.mp3": 0.60,
    "in-game.mp3": 0.45,
    "boss-intro.mp3": 0.80,
}

# Handles pygame mixer safely, fallback to avoid crash if audio doesn't work
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

# helper function to work with init audio
def is_ready():
    mixer = _get_mixer()
    return _mixer_ready and mixer is not None and mixer.get_init() is not None

# Based on the user actions on menu_settings.py (volume menu) the function handles
# the volume values and mute/unmute music/sfx
def apply_audio_settings():
    mixer = _get_mixer()
    music_base = _current_music_base_volume if _current_music_base_volume is not None else 1.0
    music_actual = 0.0 if master_muted or music_muted else music_base * music_volume
    sfx_actual = 0.0 if master_muted or sfx_muted else sfx_volume

    if is_ready() and mixer is not None:
        mixer.music.set_volume(music_actual)

    for name, sound in _sounds.items():
        sound.set_volume(SOUND_VOLUMES.get(name, 1.0) * sfx_actual)

# Loads SFX and aplies volumes to them based on menu_settings
def _register_sound(name, filename, volume):
    if not init_audio():
        return None

    # Paths for the SFX
    path = os.path.join(SOUND_FX_DIR, filename)
    
    # check if the mixer is read (machine audio available)
    mixer = _get_mixer() 
    if mixer is None:
        return None

    try:
        sound = mixer.Sound(path)
    except (pygame.error, FileNotFoundError, NotImplementedError):
        return None

    # SFX setter with volumes
    SOUND_VOLUMES[name] = volume
    _sounds[name] = sound
    apply_audio_settings()
    return sound


def play_sound(name):
    sound = _sounds.get(name)
    if sound is None:
        return None
    return sound.play()


def _resolve_audio_path(filename):
    sound_fx_path = os.path.join(SOUND_FX_DIR, filename)
    if os.path.exists(sound_fx_path):
        return sound_fx_path
    music_path = os.path.join(MUSIC_DIR, filename)
    if os.path.exists(music_path):
        return music_path
    return sound_fx_path
def load_game_sfx():
    load_sound("alien_hit", "alien-being-hit.mp3", volume=0.55)
    load_sound("boss_damage", "boss-damage.mp3", volume=0.6)
    load_sound("game_over", "game-over.mp3", volume=0.7)
    load_sound("gun_shot", "gun-shot.mp3", volume=0.45)
    load_sound("player_hit", "player-being-damaged.mp3", volume=0.6)


def _get_music_base_volume(filename, volume):
    if volume is not None:
        return max(0.0, min(1.0, volume))
    return MUSIC_VOLUMES.get(filename, 1.0)


def play_music(filename, loops=-1, volume=None):
    global _current_music, _current_music_base_volume

    if not init_audio():
        return False

    mixer = _get_mixer()
    if mixer is None:
        return False

    music_path = _resolve_audio_path(filename)

    try:
        if _current_music != music_path:
            mixer.music.load(music_path)
            _current_music = music_path
        _current_music_base_volume = _get_music_base_volume(filename, volume)
        apply_audio_settings()
        mixer.music.play(loops)
        return True
    except (pygame.error, FileNotFoundError, NotImplementedError):
        _current_music = None
        _current_music_base_volume = None
        return False


def stop_music():
    global _current_music, _current_music_base_volume

    if not is_ready():
        return

    mixer = _get_mixer()
    if mixer is None:
        return

    mixer.music.stop()
    _current_music = None
    _current_music_base_volume = None


def ensure_music(filename, loops=-1, volume=None):
    music_path = _resolve_audio_path(filename)
    if _current_music == music_path and is_music_playing():
        return True
    return play_music(filename, loops=loops, volume=volume)


def is_music_playing():
    if not is_ready():
        return False

    mixer = _get_mixer()
    if mixer is None:
        return False

    return mixer.music.get_busy()


# load the actual mp3s and set each with the volumes of SOUND VOLUMES and MUSIC VOLUMES configs (start of the file)
def load_game_sfx():
    _register_sound("alien_hit", "alien-being-hit.mp3", SOUND_VOLUMES["alien_hit"])
    _register_sound("button_click", "click-buttons.mp3", SOUND_VOLUMES["button_click"])
    _register_sound("dash", "dash.mp3", SOUND_VOLUMES["dash"])
    _register_sound("freeze", "freeze.mp3", SOUND_VOLUMES["freeze"])
    _register_sound("game_over", "game-over.mp3", SOUND_VOLUMES["game_over"])
    _register_sound("gun_shot", "gun-shot.mp3", SOUND_VOLUMES["gun_shot"])
    _register_sound("item_pickup", "item-pickup.mp3", SOUND_VOLUMES["item_pickup"])
    _register_sound("player_hit", "player-being-damaged.mp3", SOUND_VOLUMES["player_hit"])
    _register_sound("success", "success.mp3", SOUND_VOLUMES["success"])


def stop_all_sfx():
    if not is_ready():
        return
    mixer = _get_mixer()
    if mixer is None:
        return
    mixer.stop()
