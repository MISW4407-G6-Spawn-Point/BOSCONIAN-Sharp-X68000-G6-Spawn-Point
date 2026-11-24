from typing import Callable

import esper
import pygame
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


_PHASE_COLORS = {
    "GREEN": pygame.Color(0, 230, 120),
    "YELLOW": pygame.Color(230, 230, 0),
    "RED": pygame.Color(230, 0, 0),
}

_PHASE_LABELS = {
    "GREEN": "GREEN",
    "YELLOW": "YELLOW",
    "RED": "RED",
}


def system_condition(world: esper.World, delta_time: float,
                     on_phase_change: Callable[[str], None] = None) -> None:
    """Actualiza la alerta; on_phase_change recibe la nueva fase una sola vez por cambio"""
    for _, condition in world.get_component(CConditionDisplay):
        condition.elapsed_time += delta_time
        if condition.elapsed_time >= condition.red_time:
            phase = "RED"
        elif condition.elapsed_time >= condition.yellow_time:
            phase = "YELLOW"
        else:
            phase = "GREEN"

        if phase == condition.phase:
            continue

        condition.phase = phase
        bar_surface = world.component_for_entity(condition.bar_entity, CSurface)
        bar_surface.surf.fill(_PHASE_COLORS[phase])
        text_surface = world.component_for_entity(condition.text_entity, CSurface)
        font = ServiceLocator.fonts_service.get(
            condition.font_path,
            condition.text_size,
        )
        text_surface.surf = font.render(
            _PHASE_LABELS[phase],
            True,
            condition.text_color,
        )
        text_surface.area = text_surface.surf.get_rect()
        text_transform = world.component_for_entity(
            condition.text_entity,
            CTransform,
        )
        text_transform.pos = condition.text_position - pygame.Vector2(
            text_surface.surf.get_size()
        ) / 2
        if on_phase_change is not None:
            on_phase_change(phase)


def reset_condition(world: esper.World) -> None:
    for _, condition in world.get_component(CConditionDisplay):
        if condition.phase == "RED":
            continue
        condition.elapsed_time = 0.0
        condition.phase = ""
    system_condition(world, 0.0)
