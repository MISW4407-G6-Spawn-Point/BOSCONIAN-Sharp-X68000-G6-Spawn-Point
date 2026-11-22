from typing import Callable
import esper
import pygame

from src.create.prefab_creator import create_death_explosions
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.c_formation_group import CFormationGroup


def system_player_state(world:esper.World, player_entity:int, delta_time:float,
                        on_respawn:Callable[[], None]):
    """Mientras esta muerto, cuenta el tiempo y pide la escena respawn"""
    c_ps = world.component_for_entity(player_entity, CPlayerState)
    if c_ps.state == PlayerState.DEAD:
        c_ps.timer -= delta_time
        if c_ps.timer <= 0:
            on_respawn()


def kill_player(world:esper.World, player_entity:int, death_cfg:dict, explosion_cfg:dict):
    """Explosiones, la nave se detiene y se oculta"""
    c_ps = world.component_for_entity(player_entity, CPlayerState)
    c_p = world.component_for_entity(player_entity, CPlayerShip)
    c_t = world.component_for_entity(player_entity, CTransform)
    c_s = world.component_for_entity(player_entity, CSurface)
    c_v = world.component_for_entity(player_entity, CVelocity)

    create_death_explosions(world, c_t.pos + pygame.Vector2(c_s.area.size) / 2,
                            death_cfg, explosion_cfg)
    c_ps.state = PlayerState.DEAD
    c_ps.timer = c_ps.respawn_time
    c_p.active = False
    c_p.speed = 0.0
    c_v.vel = pygame.Vector2(0, 0)
    c_s.surf = pygame.Surface(c_s.area.size, pygame.SRCALPHA)


def respawn_player(world:esper.World, player_entity:int, start_pos:dict):
    """Reaparece en el punto de inicio, acelerando desde cero, y limpia los enemigos"""
    c_ps = world.component_for_entity(player_entity, CPlayerState)
    c_p = world.component_for_entity(player_entity, CPlayerShip)
    c_t = world.component_for_entity(player_entity, CTransform)
    c_s = world.component_for_entity(player_entity, CSurface)

    c_s.surf = c_p.sprites[c_p.dir_index]
    c_s.area = c_s.surf.get_rect()
    c_t.pos = pygame.Vector2(start_pos["x"], start_pos["y"]) - pygame.Vector2(c_s.area.size) / 2
    c_p.speed = 0.0
    c_p.active = True
    c_ps.state = PlayerState.ALIVE
    for group_entity, group in world.get_component(CFormationGroup):
        for member in group.members:
            if world.entity_exists(member):
                world.delete_entity(member)
        world.delete_entity(group_entity)