from typing import Callable

import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_mine_blast import CMineBlast
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_enemy_state import shortest_delta
from src.ecs.systems.s_formation import forfeit_formation_bonus

_ENEMY_TYPES = {"i", "p", "e", "spy"}


def _center(world:esper.World, entity:int) -> pygame.Vector2:
    c_t = world.component_for_entity(entity, CTransform)
    c_s = world.component_for_entity(entity, CSurface)
    return c_t.pos + pygame.Vector2(c_s.area.size) / 2


def explode_mine(world:esper.World, mine_entity:int, explosion_cfg:dict) -> None:
    """Destruye la mina con la explosion "mine"; system_mine_explosion aplica el radio letal"""
    if not world.entity_exists(mine_entity):
        return
    mine_cfg = explosion_cfg["mine"]
    blast = create_explosion(world, _center(world, mine_entity), mine_cfg)
    world.add_component(blast, CMineBlast(mine_cfg["lethal_radius"]))
    world.delete_entity(mine_entity)


def system_mine_explosion(world:esper.World, player_entity:int, world_size:dict,
                          explosion_cfg:dict, god_mode:bool,
                          on_player_hit:Callable[[], None]):
    """Mata al jugador y a los enemigos cuyo centro quede dentro del radio de la mina"""
    for blast_entity, c_mb in list(world.get_component(CMineBlast)):
        center = _center(world, blast_entity)

        pl_state = world.component_for_entity(player_entity, CPlayerState)
        if not god_mode and pl_state.state == PlayerState.ALIVE:
            if shortest_delta(center, _center(world, player_entity), world_size).length() \
                    <= c_mb.radius:
                on_player_hit()

        for entity, c_lo in world.get_component(CLevelObject):
            if c_lo.object_type not in _ENEMY_TYPES or not world.entity_exists(entity):
                continue
            enemy_center = _center(world, entity)
            if shortest_delta(center, enemy_center, world_size).length() > c_mb.radius:
                continue
            create_explosion(world, enemy_center, explosion_cfg,
                             world.component_for_entity(entity, CVelocity).vel)
            forfeit_formation_bonus(world, entity)
            world.delete_entity(entity)

        world.remove_component(blast_entity, CMineBlast)
