from typing import Callable
import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_hitbox import CHitBox
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform


def system_collision_player(world:esper.World, player_entity:int, explosion_cfg:dict,
                            on_player_hit:Callable[[], None]):
    """El jugador choca con enemigos, rocas, minas o bases el objeto explota y suma puntos, el jugador muere"""
    pl_state = world.component_for_entity(player_entity, CPlayerState)
    if pl_state.state != PlayerState.ALIVE:
        return
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_h = world.component_for_entity(player_entity, CHitBox)
    pl_rect = pl_h.get_rect(pl_t.pos, pl_s.area.size)

    for entity, (c_lo, c_t, c_s) in world.get_components(CLevelObject, CTransform, CSurface):
        if c_lo.object_type == "enemy_base":
            combat = world.component_for_entity(entity, CEnemyBaseCombat)
            if _hits_base(pl_rect, c_t.pos, combat):
                on_player_hit()
                return
            continue

        c_h = world.try_component(entity, CHitBox)
        if c_h is not None:
            obj_rect = c_h.get_rect(c_t.pos, c_s.area.size)
        else:
            obj_rect = CSurface.get_area_relative(c_s.area, c_t.pos)

        if pl_rect.colliderect(obj_rect):
            create_explosion(world, pygame.Vector2(obj_rect.center), explosion_cfg)
            _add_score(world, c_lo.score)
            world.delete_entity(entity)
            on_player_hit()
            return


def _hits_base(pl_rect:pygame.Rect, base_pos:pygame.Vector2, combat:CEnemyBaseCombat) -> bool:
    """Misma geometria que usa la colision de balas: 6 nodos y el ojo central"""
    if pl_rect.colliderect(combat.get_eye_rect(base_pos)):
        return True
    for index in range(len(combat.node_centers)):
        if combat.node_destroyed[index]:
            continue
        if pl_rect.colliderect(combat.get_node_rect(base_pos, index)):
            return True
    return False


def _add_score(world:esper.World, points:int):
    for _, score_display in world.get_component(CScoreDisplay):
        if score_display.tracks_score:
            score_display.value += points