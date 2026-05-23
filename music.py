import pygame
import os

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.enabled = False
        self.file = ""
        self.volume = 0.5
        self.playing = False

    def set_file(self, file_path: str):
        self.file = file_path

    def set_volume(self, vol: float):
        self.volume = vol
        pygame.mixer.music.set_volume(vol)

    def play(self):
        if not self.enabled or not self.file or not os.path.exists(self.file):
            return
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play(-1)
        self.playing = True

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def resume(self):
        if self.enabled and self.file and not self.playing:
            pygame.mixer.music.unpause()
            self.playing = True

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.play()
        else:
            self.stop()