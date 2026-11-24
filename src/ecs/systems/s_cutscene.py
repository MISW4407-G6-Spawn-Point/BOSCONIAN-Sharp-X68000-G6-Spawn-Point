from typing import Callable

import esper
import pygame

from src.ecs.components.c_cutscene import CCutscene


def system_cutscene(world:esper.World, delta_time:float,
                    on_end:Callable[[], None]) -> pygame.Vector2:
    """Avanza la cutscene; devuelve el desplazamiento de estrellas o None si no hay cutscene"""
    for entity, c_c in world.get_component(CCutscene):
        c_c.time_left -= delta_time
        if c_c.time_left <= 0:
            world.delete_entity(entity)
            on_end()
            return None
        factor = min(1.0, c_c.time_left / c_c.slowdown_time) if c_c.slowdown_time > 0 else 1.0
        return c_c.direction * c_c.star_speed * factor * delta_time
    return None
