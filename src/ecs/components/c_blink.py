import pygame

class CBlink:
    """Alterna entre dos superficies (visible / invisible).
    El tiempo de cada fase se sortea entre interval_min e interval_max."""

    def __init__(self, on_surf:pygame.Surface, interval_min:float, interval_max:float = None) -> None:
        self.on_surf = on_surf
        self.off_surf = pygame.Surface(on_surf.get_size(), pygame.SRCALPHA)
        self.interval_min = interval_min
        self.interval_max = interval_min if interval_max is None else interval_max
        self.time = interval_min
        self.visible = True