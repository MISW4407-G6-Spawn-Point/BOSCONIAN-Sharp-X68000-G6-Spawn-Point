import pygame


class CCutscene:
    """Cutscene de inicio de nivel: mientras exista, el juego no avanza
    direction: hacia donde apunta la nave (las estrellas van al reves)"""

    def __init__(self, duration:float, star_speed:float, slowdown_time:float,
                 direction:pygame.Vector2) -> None:
        self.time_left = duration
        self.star_speed = star_speed
        self.slowdown_time = slowdown_time
        self.direction = pygame.Vector2(direction)
