import pygame


class CCamera:
    """Camara que sigue a jugador dentro del mundo que se repite
    view: rectangulo de pantalla donde se dibuja el mundo
    world_size: tamano total del mundo antes de repetirse"""

    def __init__(self, target:int, view:pygame.Rect, world_size:pygame.Vector2) -> None:
        self.target = target
        self.view = view
        self.world_size = world_size
        self.pos = pygame.Vector2(0, 0)
        self.delta = pygame.Vector2(0, 0)