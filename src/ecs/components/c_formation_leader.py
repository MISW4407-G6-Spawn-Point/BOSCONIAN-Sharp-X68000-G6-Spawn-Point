import pygame


class CFormationLeader:
    """Capitan de la formacion: persigue al jugador y el resto lo sigue"""

    def __init__(self, heading:pygame.Vector2, speed:float, turn_rate:float,
                 sprites:list) -> None:
        self.heading = heading
        self.speed = speed
        self.turn_rate = turn_rate
        self.sprites = sprites
        self.dir_index = -1