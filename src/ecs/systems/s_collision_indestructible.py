from typing import Callable

import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_indestructible import CTagIndestructible
from src.ecs.systems.s_collision_enemy_obstacle import ENEMY_TYPES, hit_rect
from src.ecs.systems.s_enemy_state import wrapped_overlap
from src.ecs.systems.s_formation import forfeit_formation_bonus


def _bounce_on_bases(world:esper.World, rock:int, world_size:dict):
    """Rebota contra el ojo y los nodos vivos de las bases sin danarlas"""
    c_t = world.component_for_entity(rock, CTransform)
    c_v = world.component_for_entity(rock, CVelocity)
    for _, (combat, b_t) in world.get_components(CEnemyBaseCombat, CTransform):
        rects = [combat.get_eye_rect(b_t.pos)]
        rects += [combat.get_node_rect(b_t.pos, index)
                  for index in range(len(combat.node_centers))
                  if not combat.node_destroyed[index]]
        for rect in rects:
            push = wrapped_overlap(hit_rect(world, rock), rect, world_size)
            if push is None:
                continue
            c_t.pos += push
            normal = push.normalize()
            if c_v.vel.dot(normal) < 0:
                c_v.vel = c_v.vel.reflect(normal)
            return


def system_collision_indestructible(world:esper.World, player_entity:int, world_size:dict,
                                    explosion_cfg:dict, god_mode:bool,
                                    on_player_hit:Callable[[], None]):
    """La roca indestructible mata al jugador y a los enemigos, frena todas las balas
    y rebota en las bases. Rocas y minas no le afectan."""
    pl_state = world.component_for_entity(player_entity, CPlayerState)

    for rock, _ in world.get_component(CTagIndestructible):
        _bounce_on_bases(world, rock, world_size)
        rock_rect = hit_rect(world, rock)

        if not god_mode and pl_state.state == PlayerState.ALIVE and \
                wrapped_overlap(rock_rect, hit_rect(world, player_entity), world_size):
            on_player_hit()

        for entity, c_lo in world.get_component(CLevelObject):
            if c_lo.object_type not in ENEMY_TYPES or not world.entity_exists(entity):
                continue
            enemy_rect = hit_rect(world, entity)
            if wrapped_overlap(rock_rect, enemy_rect, world_size) is None:
                continue
            create_explosion(world, pygame.Vector2(enemy_rect.center), explosion_cfg,
                             world.component_for_entity(entity, CVelocity).vel)
            forfeit_formation_bonus(world, entity)
            world.delete_entity(entity)

        for tag in (CTagBullet, CTagEnemyBullet):
            for bullet, _ in world.get_component(tag):
                if wrapped_overlap(rock_rect, hit_rect(world, bullet), world_size):
                    world.delete_entity(bullet)
