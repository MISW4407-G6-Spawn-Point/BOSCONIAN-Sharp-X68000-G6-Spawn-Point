import pygame


class CFormationGroup:
    """Una formacion completa (lider + 4). Sirve para saber si el jugador la destruyo toda"""

    def __init__(self, members:list, bonus:int) -> None:
        self.members = list(members)
        self.bonus = bonus
        self.escaped = False          
        self.last_center = pygame.Vector2(0, 0)