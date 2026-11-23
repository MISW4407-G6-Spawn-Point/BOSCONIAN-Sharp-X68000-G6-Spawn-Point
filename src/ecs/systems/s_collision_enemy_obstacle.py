import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_hitbox import CHitBox
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_enemy_state import wrapped_overlap
from src.ecs.systems.s_formation import forfeit_formation_bonus

ENEMY_TYPES = {"i", "p", "e", "spy"}
_OBSTACLE_TYPES = {"1-a", "1-b", "1-c", "2-a", "2-b", "2-c", "mine"}


def hit_rect(world:esper.World, entity:int) -> pygame.Rect:
    """Rect de colision: CHitBox si tiene, si no el sprite"""
    c_t = world.component_for_entity(entity, CTransform)
    c_s = world.component_for_entity(entity, CSurface)
    c_h = world.try_component(entity, CHitBox)
    if c_h is not None:
        return c_h.get_rect(c_t.pos, c_s.area.size)
    return CSurface.get_area_relative(c_s.area, c_t.pos)


def system_collision_enemy_obstacle(world:esper.World, world_size:dict, explosion_cfg:dict):
    """Enemigo contra roca o mina: ambos explotan, sin puntaje para el jugador"""
    enemies = []
    obstacles = []
    for entity, c_lo in world.get_component(CLevelObject):
        if c_lo.object_type in ENEMY_TYPES:
            enemies.append(entity)
        elif c_lo.object_type in _OBSTACLE_TYPES:
            obstacles.append(entity)

    for enemy in enemies:
        enemy_rect = hit_rect(world, enemy)
        for obstacle in obstacles:
            if not world.entity_exists(obstacle):
                continue
            obstacle_rect = hit_rect(world, obstacle)
            if wrapped_overlap(enemy_rect, obstacle_rect, world_size) is None:
                continue
            create_explosion(world, pygame.Vector2(enemy_rect.center), explosion_cfg,
                             world.component_for_entity(enemy, CVelocity).vel)
            create_explosion(world, pygame.Vector2(obstacle_rect.center), explosion_cfg)
            forfeit_formation_bonus(world, enemy)
            world.delete_entity(enemy)
            world.delete_entity(obstacle)
            break
