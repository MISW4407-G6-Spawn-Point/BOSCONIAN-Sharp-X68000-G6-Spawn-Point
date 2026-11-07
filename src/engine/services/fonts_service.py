import pygame


class FontsService:
    """Carga y guarda en cache las fuentes .ttf (una por ruta y tamano)."""

    def __init__(self) -> None:
        self._fonts = {}

    def get(self, path: str, size: int) -> pygame.font.Font:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(path, size)
        return self._fonts[key]
