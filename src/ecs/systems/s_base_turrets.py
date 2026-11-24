import random

import esper
import pygame

from src.create.prefab_creator import create_enemy_bullet
from src.ecs.components.c_base_turrets import CBaseTurrets
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.systems.s_enemy_state import shortest_delta


def system_base_turrets(world:esper.World, player_entity:int, world_size:dict,
                        enemy_bullet_cfg:dict, delta_time:float):
    """Cada torreta viva cerca del jugador le dispara cuando vence su temporizador"""
    pl_state = world.component_for_entity(player_entity, CPlayerState)
    if pl_state.state != PlayerState.ALIVE:
        return
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    c_bt:CBaseTurrets
    for _, (c_bt, combat, c_t) in world.get_components(CBaseTurrets, CEnemyBaseCombat,
                                                        CTransform):
        for index in range(len(combat.node_centers)):
            if combat.node_destroyed[index]:
                continue
            turret_center = combat.get_node_center(c_t.pos, index)
            to_player = shortest_delta(turret_center, player_center, world_size)
            if to_player.length() > enemy_bullet_cfg["range"] or to_player.length_squared() == 0:
                continue
            c_bt.timers[index] -= delta_time
            if c_bt.timers[index] <= 0:
                create_enemy_bullet(world, turret_center, to_player.normalize(),
                                    enemy_bullet_cfg)
                c_bt.shots_left[index] -= 1
                if c_bt.shots_left[index] > 0:
                    c_bt.timers[index] = c_bt.burst_gap
                else:
                    c_bt.shots_left[index] = c_bt.burst
                    c_bt.timers[index] = random.uniform(c_bt.interval_min, c_bt.interval_max)
