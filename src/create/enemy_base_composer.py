from collections.abc import Sequence
from typing import Optional, Tuple

import pygame


DEFAULT_MODULE_CENTERS = (
    pygame.Vector2(36, 15),
    pygame.Vector2(62, 15),
    pygame.Vector2(20, 40),
    pygame.Vector2(79, 40),
    pygame.Vector2(36, 65),
    pygame.Vector2(62, 65),
)
DEFAULT_CORE_CENTER = pygame.Vector2(49, 40)
DEFAULT_LEFT_SUPPORT_POSITION = pygame.Vector2(21, 19)
DEFAULT_RIGHT_SUPPORT_POSITION = pygame.Vector2(65, 19)
DEFAULT_LEFT_CONNECTOR_POSITION = pygame.Vector2(30, 38)
DEFAULT_RIGHT_CONNECTOR_POSITION = pygame.Vector2(61, 38)


def _blit_centered(
    destination_surface: pygame.Surface,
    source_surface: pygame.Surface,
    center_position: pygame.Vector2,
) -> None:
    destination_position = center_position - pygame.Vector2(
        source_surface.get_size()
    ) / 2
    destination_surface.blit(source_surface, destination_position)


def enemy_base_composer(
    left_support_surface: pygame.Surface,
    right_support_surface: pygame.Surface,
    left_connector_surface: pygame.Surface,
    right_connector_surface: pygame.Surface,
    eye_sprite: pygame.Surface,
    upper_left_module_sprite: pygame.Surface,
    upper_right_module_sprite: pygame.Surface,
    middle_left_module_sprite: pygame.Surface,
    middle_right_module_sprite: pygame.Surface,
    lower_left_module_sprite: pygame.Surface,
    lower_right_module_sprite: pygame.Surface,
    destination_size: Optional[Tuple[int, int]] = (99, 80),
    module_centers: Sequence[pygame.Vector2] = DEFAULT_MODULE_CENTERS,
    core_center: pygame.Vector2 = DEFAULT_CORE_CENTER,
    left_support_position: pygame.Vector2 = DEFAULT_LEFT_SUPPORT_POSITION,
    right_support_position: pygame.Vector2 = DEFAULT_RIGHT_SUPPORT_POSITION,
    left_connector_position: pygame.Vector2 = DEFAULT_LEFT_CONNECTOR_POSITION,
    right_connector_position: pygame.Vector2 = DEFAULT_RIGHT_CONNECTOR_POSITION,
) -> pygame.Surface:
    """Construye la base con soportes, seis nodos y el ojo central."""
    if len(module_centers) != 6:
        raise ValueError("module_centers debe contener exactamente seis posiciones")
    if destination_size is None or destination_size[0] <= 0 or destination_size[1] <= 0:
        raise ValueError("destination_size debe tener dimensiones positivas")

    assembled_base_surface = pygame.Surface(destination_size, pygame.SRCALPHA)
    assembled_base_surface.blit(left_support_surface, left_support_position)
    assembled_base_surface.blit(right_support_surface, right_support_position)
    assembled_base_surface.blit(left_connector_surface, left_connector_position)
    assembled_base_surface.blit(right_connector_surface, right_connector_position)

    module_sprites = (
        upper_left_module_sprite,
        upper_right_module_sprite,
        middle_left_module_sprite,
        middle_right_module_sprite,
        lower_left_module_sprite,
        lower_right_module_sprite,
    )
    for module_sprite, module_center in zip(module_sprites, module_centers):
        _blit_centered(assembled_base_surface, module_sprite, module_center)

    _blit_centered(assembled_base_surface, eye_sprite, core_center)
    return assembled_base_surface
