import pygame


class CFormationMember:
    """Nave de la formacion posicion relativa al lide| Si el lider muere, deja de seguirlo y huye"""

    def __init__(self, leader:int, offset:pygame.Vector2, sprites:list,
                 flee_speed:float) -> None:
        self.leader = leader
        self.offset = offset
        self.sprites = sprites
        self.flee_speed = flee_speed
        self.fleeing = False
        self.heading = pygame.Vector2(0, -1)
        self.dir_index = -1