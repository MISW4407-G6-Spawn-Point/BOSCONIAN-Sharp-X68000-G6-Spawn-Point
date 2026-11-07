import pygame

class CSurface:
    def __init__(self, size:pygame.Vector2, color:pygame.Color) -> None:
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        self.area = self.surf.get_rect()

    @classmethod
    def from_surface(cls, surface:pygame.Surface):
        c_surface = cls(pygame.Vector2(0,0), pygame.Color(0,0,0))
        c_surface.surf = surface
        c_surface.area = surface.get_rect()
        return c_surface

    @classmethod
    def from_text(cls, text:str, font:pygame.font.Font, color:pygame.Color):
        """Crea una superficie a partir de un texto, una fuente y un color."""
        return cls.from_surface(font.render(text, True, color))

    def get_area_relative(area:pygame.Rect, pos_topleft:pygame.Vector2):
        new_rect = area.copy()
        new_rect.topleft = pos_topleft.copy()
        return new_rect
