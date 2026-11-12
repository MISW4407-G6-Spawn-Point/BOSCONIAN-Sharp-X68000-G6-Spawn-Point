import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform


def _wrap_delta(value:float, size:float) -> float:
    """Lleva una diferencia al rango (camino mas corto cuando el mundo se repite)"""
    return (value + size / 2) % size - size / 2


def system_camera(world:esper.World):
    c_c:CCamera
    for _, c_c in world.get_component(CCamera):
        if not world.entity_exists(c_c.target):
            c_c.delta = pygame.Vector2(0, 0)
            continue
        t_t = world.component_for_entity(c_c.target, CTransform)
        t_s = world.component_for_entity(c_c.target, CSurface)
        target_center = t_t.pos + pygame.Vector2(t_s.area.size) / 2
        new_pos = target_center - pygame.Vector2(c_c.view.size) / 2

        c_c.delta = pygame.Vector2(_wrap_delta(new_pos.x - c_c.pos.x, c_c.world_size.x),
                                   _wrap_delta(new_pos.y - c_c.pos.y, c_c.world_size.y))
        c_c.pos = pygame.Vector2(new_pos.x % c_c.world_size.x,
                                 new_pos.y % c_c.world_size.y)


def world_to_screen(c_c:CCamera, pos:pygame.Vector2) -> pygame.Vector2:
    """Posicion en pantalla de algo gdel mundo, eliiendo la copia mas cercana a la camara"""
    half_view = pygame.Vector2(c_c.view.size) / 2
    rel = pygame.Vector2(_wrap_delta(pos.x - c_c.pos.x - half_view.x, c_c.world_size.x),
                         _wrap_delta(pos.y - c_c.pos.y - half_view.y, c_c.world_size.y))
    return pygame.Vector2(c_c.view.topleft) + half_view + rel