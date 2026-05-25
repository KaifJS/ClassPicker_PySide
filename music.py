# music.py
import pygame
import os
import random
from typing import List, Optional

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.enabled = False
        self.playlist: List[str] = []          # 音乐文件路径列表
        self.current_index = 0
        self.mode = "order"                    # order, shuffle, single, loop_one
        self.volume = 0.5
        self.playing = False
        self._is_looping = False               # 内部标志

    def set_playlist(self, folder_path: str):
        """扫描文件夹，支持 mp3/wav/ogg/flac 等"""
        if not os.path.isdir(folder_path):
            return
        supported = ('.mp3', '.wav', '.ogg', '.flac')
        self.playlist = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(supported)
        ]
        self.current_index = 0
        if self.mode == "shuffle":
            random.shuffle(self.playlist)
        # 如果当前有播放且启用，自动开始播放第一首
        if self.enabled and self.playlist:
            self.play()

    def set_mode(self, mode: str):
        """mode: 'order', 'shuffle', 'single', 'loop_one'"""
        self.mode = mode
        if mode == "shuffle" and self.playlist:
            # 随机模式：打乱剩余列表（但不改变当前播放）
            current = self.playlist[self.current_index] if self.playlist else None
            random.shuffle(self.playlist)
            if current and current in self.playlist:
                self.current_index = self.playlist.index(current)

    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))
        pygame.mixer.music.set_volume(self.volume)

    def play(self):
        if not self.enabled or not self.playlist:
            return
        if self.playing:
            self.stop()
        file = self.playlist[self.current_index]
        if not os.path.exists(file):
            self._next()
            return
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def resume(self):
        if self.enabled and not self.playing and self.playlist:
            pygame.mixer.music.unpause()
            self.playing = True

    def next(self):
        """下一首"""
        if not self.playlist:
            return
        if self.mode == "single":
            # 单曲模式：重新播放当前曲目
            self.play()
            return
        if self.mode == "loop_one":
            # 单曲循环：重新播放当前曲目
            self.play()
            return
        self._next()
        self.play()

    def _next(self):
        if not self.playlist:
            return
        if self.mode == "shuffle":
            # 随机模式：随机抽取下一首
            if len(self.playlist) > 1:
                new_index = self.current_index
                while new_index == self.current_index:
                    new_index = random.randrange(len(self.playlist))
                self.current_index = new_index
            else:
                self.current_index = 0
        else:  # order
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous(self):
        if not self.playlist:
            return
        if self.mode == "shuffle":
            # 随机模式：随机跳转
            new_index = random.randrange(len(self.playlist))
            self.current_index = new_index
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def on_finished(self):
        """音乐播放结束时的回调"""
        if not self.playlist:
            return
        if self.mode == "loop_one":
            # 单曲循环：重新播放同一首
            self.play()
        elif self.mode == "single":
            # 单次播放：停止
            self.stop()
        else:
            self._next()