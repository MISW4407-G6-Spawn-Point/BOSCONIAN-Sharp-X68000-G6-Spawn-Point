from typing import Callable

import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_hitbox import CHitBox
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet

# Naves enemigas (sueltas, de formacion y espia): explotan con la bala, sin puntaje
_ENEMY_TYPES = {"i", "p", "e", "spy"}
# Rocas y minas: solo detienen la bala
_OBSTACLE_TYPES = {"1-a", "1-b", "1-c", "2-a", "2-b", "2-c", "mine"}


def _object_rect(world:esper.World, entity:int, c_t:CTransform, c_s:CSurface) -> pygame.Rect:
    c_h = world.try_component(entity, CHitBox)
    if c_h is not None:
        return c_h.get_rect(c_t.pos, c_s.area.size)
    return CSurface.get_area_relative(c_s.area, c_t.pos)


def system_collision_enemy_bullet(world:esper.World, player_entity:int, explosion_cfg:dict,
                                  god_mode:bool, on_player_hit:Callable[[], None]):
    """Balas de torreta contra el jugador, naves enemigas, rocas y minas"""
    pl_state = world.component_for_entity(player_entity, CPlayerState)
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_rect = world.component_for_entity(player_entity, CHitBox).get_rect(pl_t.pos,
                                                                          pl_s.area.size)
    objects = list(world.get_components(CLevelObject, CTransform, CSurface))
    hit_objects = set()

    for bullet_entity, (_, b_t, b_s) in world.get_components(CTagEnemyBullet, CTransform,
                                                             CSurface):
        bullet_rect = CSurface.get_area_relative(b_s.area, b_t.pos)

        # Jugador: muere salvo en modo invencible (ahi la bala lo atraviesa)
        if not god_mode and pl_state.state == PlayerState.ALIVE \
                and bullet_rect.colliderect(pl_rect):
            world.delete_entity(bullet_entity)
            on_player_hit()
            continue

        for entity, (c_lo, c_t, c_s) in objects:
            if entity in hit_objects:
                continue
            is_enemy = c_lo.object_type in _ENEMY_TYPES
            if not is_enemy and c_lo.object_type not in _OBSTACLE_TYPES:
                continue  # la base que dispara no se dana con sus balas
            obj_rect = _object_rect(world, entity, c_t, c_s)
            if not bullet_rect.colliderect(obj_rect):
                continue
            world.delete_entity(bullet_entity)
            if is_enemy:
                create_explosion(world, pygame.Vector2(obj_rect.center), explosion_cfg)
                world.delete_entity(entity)
                hit_objects.add(entity)
            break
