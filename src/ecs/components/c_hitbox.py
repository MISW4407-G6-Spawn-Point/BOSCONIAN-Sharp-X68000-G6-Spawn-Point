import pygame


class CHitBox:
    """Area de colision centrada en el sprite.
    Es mas pequena que la imagen, no cambia al rotar la nave"""

    def __init__(self, hitbox_cfg:dict) -> None:
        self.size = pygame.Vector2(hitbox_cfg["w"], hitbox_cfg["h"])

    def get_rect(self, pos:pygame.Vector2, sprite_size) -> pygame.Rect:
        center = pos + pygame.Vector2(sprite_size) / 2
        return pygame.Rect(center - self.size / 2, self.size)