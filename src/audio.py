import pygame
import os
from src.settings import ASSET_SND

# wraps all the sound stuff so main game doesn't have to worry about it

class AudioManager:
    def __init__(self):
        self.enabled      = True
        self.music_on     = True
        self.sounds       = {}
        self._load_sounds()
        self._start_music()

    def _load_sounds(self):
        sfx_files = {
            "collect":   "collect.wav",
            "hit":       "hit.wav",
            "explosion": "explosion.wav",
            "levelup":   "levelup.wav",
        }
        for key, fname in sfx_files.items():
            path = os.path.join(ASSET_SND, fname)
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(0.55)
                self.sounds[key] = snd
            except Exception as e:
                print(f"  Audio: couldn't load {fname}: {e}")

    def _start_music(self):
        # try .mp3 first, then .wav
        for fname in ("music.wav", "music.mp3", "music.ogg"):
            path = os.path.join(ASSET_SND, fname)
            if os.path.exists(path) and os.path.getsize(path) > 5000:
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(0.35)
                    pygame.mixer.music.play(-1)   # loop forever
                    print(f"  Music loaded: {fname}")
                    return
                except Exception as e:
                    print(f"  Music load failed ({fname}): {e}")
        print("  No music file found, continuing in silence")

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        return self.music_on
