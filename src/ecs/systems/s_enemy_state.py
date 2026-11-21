import math
import random
import esper
import pygame

from src.ecs.components.c_enemy_state import CEnemyState, EnemyState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


def shortest_delta(origin:pygame.Vector2, target:pygame.Vector2,
                   world_size:dict) -> pygame.Vector2:
    """Vector de origin a target por el camino mas corto"""
    w, h = world_size["w"], world_size["h"]
    d = target - origin
    return pygame.Vector2((d.x + w / 2) % w - w / 2, (d.y + h / 2) % h - h / 2)


def system_enemy_state(world:esper.World, player_entity:int, world_size:dict,
                       despawn_distance:float, delta_time:float):
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    c_t:CTransform
    c_v:CVelocity
    c_s:CSurface
    c_e:CEnemyState
    for entity, (c_t, c_v, c_s, c_e) in world.get_components(CTransform, CVelocity,
                                                             CSurface, CEnemyState):
        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        to_player = shortest_delta(center, player_center, world_size)
        if to_player.length() > despawn_distance:
            world.delete_entity(entity)
            continue

        c_e.timer += delta_time
        if c_e.state == EnemyState.CHASE:
            _do_chase_state(c_e, to_player, delta_time)
        elif c_e.state == EnemyState.WANDER:
            _do_wander_state(c_e)

        c_v.vel = c_e.heading * c_e.speed
        _update_sprite(c_t, c_s, c_e)


def _do_chase_state(c_e:CEnemyState, to_player:pygame.Vector2, delta_time:float):
    _steer(c_e, to_player, delta_time)
    if c_e.timer >= c_e.chase_time:
        c_e.timer = 0.0
        if c_e.behaviour == "chase_then_leave":
            c_e.state = EnemyState.LEAVE
        elif c_e.behaviour == "chase_then_wander":
            c_e.state = EnemyState.WANDER


def _do_wander_state(c_e:CEnemyState):
    if c_e.timer >= c_e.wander_interval:
        c_e.timer = 0.0
        c_e.heading = c_e.heading.rotate(random.uniform(-90, 90))


def _steer(c_e:CEnemyState, desired:pygame.Vector2, delta_time:float):
    """seek: gira el heading hacia el objetivo con un giro maximo por seg"""
    if desired.length_squared() == 0:
        return
    angle = (c_e.heading.angle_to(desired) + 180) % 360 - 180
    max_turn = c_e.turn_rate * delta_time
    c_e.heading = c_e.heading.rotate(max(-max_turn, min(max_turn, angle)))


def _update_sprite(c_t:CTransform, c_s:CSurface, c_e:CEnemyState):
    """Elige uno de los sprites segun direccion"""
    angle = math.degrees(math.atan2(c_e.heading.x, -c_e.heading.y)) % 360
    new_index = round(angle / 45) % 8
    if new_index == c_e.dir_index:
        return
    center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
    c_e.dir_index = new_index
    c_s.surf = c_e.sprites[new_index]
    c_s.area = c_s.surf.get_rect()
    c_t.pos = center - pygame.Vector2(c_s.area.size) / 2