from typing import Callable

import esper
import pygame

from src.ecs.components.c_demo_pilot import CDemoPilot
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.systems.s_enemy_state import shortest_delta
from src.ecs.systems.s_player_ship import DIRECTIONS


def _center(world: esper.World, entity: int) -> pygame.Vector2:
    c_t = world.component_for_entity(entity, CTransform)
    c_s = world.component_for_entity(entity, CSurface)
    return c_t.pos + pygame.Vector2(c_s.area.size) / 2


def _nearest_base(world: esper.World, origin: pygame.Vector2, world_size: dict):
    """Vector (con wraparound) hacia el nucleo de la base viva mas cercana"""
    best = None
    for _, (combat, c_t) in world.get_components(CEnemyBaseCombat, CTransform):
        delta = shortest_delta(origin, combat.get_core_center(c_t.pos), world_size)
        if best is None or delta.length() < best.length():
            best = delta
    return best


def _threat(world: esper.World, origin: pygame.Vector2, heading: pygame.Vector2,
            world_size: dict, distance: float):
    """Roca, mina o enemigo cercano y adelante de la nave"""
    for entity, c_lo in world.get_component(CLevelObject):
        if c_lo.object_type == "enemy_base" or not world.entity_exists(entity):
            continue
        delta = shortest_delta(origin, _center(world, entity), world_size)
        if 0 < delta.length() < distance and delta.normalize().dot(heading) > 0.5:
            return delta
    return None


def system_demo_pilot(world: esper.World, player_entity: int, world_size: dict,
                      delta_time: float, on_fire: Callable[[], None]):
    """Maneja la nave de la demo escribiendo CPlayerShip.input y disparando a intervalos"""
    pilot = world.component_for_entity(player_entity, CDemoPilot)
    c_p = world.component_for_entity(player_entity, CPlayerShip)
    origin = _center(world, player_entity)
    heading = DIRECTIONS[c_p.dir_index]

    threat = _threat(world, origin, heading, world_size, pilot.avoid_distance)
    if threat is not None:
        side = heading.rotate(90)
        c_p.input = -side if side.dot(threat) > 0 else side
        pilot.turn_timer = pilot.turn_interval
    else:
        pilot.turn_timer -= delta_time
        if pilot.turn_timer <= 0:
            pilot.turn_timer = pilot.turn_interval
            target = _nearest_base(world, origin, world_size)
            if target is not None and target.length_squared() > 0:
                c_p.input = target.normalize()

    pilot.fire_timer -= delta_time
    if pilot.fire_timer <= 0:
        pilot.fire_timer = pilot.fire_interval
        on_fire()
