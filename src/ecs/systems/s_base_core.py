import os

import esper
import pygame

from src.create.prefab_creator import create_enemy
from src.ecs.components.c_base_core import CBaseCore
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_enemy_base_eye import CEnemyBaseEye
from src.ecs.components.c_launched_by import CLaunchedBy
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.systems.s_enemy_state import shortest_delta
from src.engine.service_locator import ServiceLocator


def _is_green(world:esper.World) -> bool:
    for _, condition in world.get_component(CConditionDisplay):
        return condition.phase == "GREEN"
    return False


def system_base_core(world:esper.World, player_entity:int, world_size:dict,
                     enemies_cfg:dict, player_speed:float):
    """En modo "cycle", cada vez que el nucleo se abre lanza un E por el eje de la base,
    hacia el lado del jugador. No lanza en VERDE ni con el jugador muerto."""
    pl_state = world.component_for_entity(player_entity, CPlayerState)
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    for base_entity, (core, eye, combat, c_t) in world.get_components(
            CBaseCore, CEnemyBaseEye, CEnemyBaseCombat, CTransform):
        if core.mode != "cycle":
            continue
        if combat.eye_frame_index != eye.open_frame:
            core.launched = False
            continue
        if core.launched:
            continue
        core.launched = True
        if pl_state.state != PlayerState.ALIVE or _is_green(world):
            continue

        core_center = combat.get_core_center(c_t.pos)
        axis = combat.get_axis()
        if shortest_delta(core_center, player_center, world_size).dot(axis) < 0:
            axis = -axis
        speed = player_speed * enemies_cfg["types"]["e"]["speed_factor"]
        enemy = create_enemy(world, core_center, "e", enemies_cfg, axis, speed,
                             enemies_cfg["default_spawn"]["accuracy"])
        world.add_component(enemy, CLaunchedBy(base_entity))
        sound = enemies_cfg.get("core_launch_sound")
        if sound and os.path.exists(sound):
            ServiceLocator.sounds_service.play(sound)
