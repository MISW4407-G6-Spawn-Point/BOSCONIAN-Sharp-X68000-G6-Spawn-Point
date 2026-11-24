import os

import pygame


class SoundService:
    """Carga, guarda en cache y reproduce los efectos de sonido."""

    def __init__(self) -> None:
        self._sounds = {}
        self._current_music = None

    def get(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        return self._sounds[path]

    def play(self, path: str, volume: float = 1.0) -> None:
        """Si el archivo no existe o no carga, no suena (no rompe el juego)"""
        if not path or not os.path.exists(path):
            return
        try:
            sound = self.get(path)
        except pygame.error:
            return
        sound.set_volume(volume)
        sound.play()

    def play_cfg(self, sound_cfg) -> None:
        """Sonido de config: {"path": ..., "volume": ...} o solo la ruta"""
        if isinstance(sound_cfg, dict):
            self.play(sound_cfg.get("path"), sound_cfg.get("volume", 1.0))
        elif sound_cfg:
            self.play(sound_cfg)

    def play_music(self, path: str, volume: float = 0.5) -> None:
        """Musica de fondo en bucle. Si ya esta sonando esa pista, no la reinicia."""
        if path == self._current_music or not os.path.exists(path):
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        self._current_music = path

    def stop_music(self) -> None:
        pygame.mixer.music.stop()
        self._current_music = None

    def pause_music(self) -> None:
        pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        pygame.mixer.music.unpause()
