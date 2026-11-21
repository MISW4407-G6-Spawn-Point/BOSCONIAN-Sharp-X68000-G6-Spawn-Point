import pygame


class CSpy:
    """Nave espia: cruza la pantalla, rebota una vez en el borde y luego se va.
    Si se escapa, la alerta pasa a ROJA."""

    def __init__(self, heading:pygame.Vector2, speed:float, score_steps:list) -> None:
        self.heading = heading
        self.speed = speed
        self.score_steps = score_steps
        self.bounced = False