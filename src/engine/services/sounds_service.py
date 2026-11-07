import pygame


class SoundService:
    """Carga, guarda en cache y reproduce los efectos de sonido."""

    def __init__(self) -> None:
        self._sounds = {}

    def get(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        return self._sounds[path]

    def play(self, path: str, volume: float = 1.0) -> None:
        sound = self.get(path)
        sound.set_volume(volume)
        sound.play()
