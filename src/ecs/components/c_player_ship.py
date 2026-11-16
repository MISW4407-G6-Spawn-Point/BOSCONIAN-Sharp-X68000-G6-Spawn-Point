import pygame


class CPlayerShip:
    """Movimiento de la nave siempre avanza hacia donde apunta,
    gira en 8 direcciones con las flechas
    sprites: las 8 superficies pre-rotadas"""

    def __init__(self, sprites:list, max_speed:float, acceleration:float,
                 start_dir:int) -> None:
        self.sprites = sprites
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.speed = 0.0
        self.dir_index = start_dir
        self.input = pygame.Vector2(0, 0)