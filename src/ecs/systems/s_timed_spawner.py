import random
import esper

from src.create.prefab_creator import create_formation, create_spy
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_formation_group import CFormationGroup
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_timed_spawner import CTimedSpawner
from src.ecs.systems.s_enemy_spawner import current_condition
from src.engine.service_locator import ServiceLocator


def system_timed_spawner(world:esper.World, player_entity:int, camera:CCamera,
                         formations_cfg:dict, spy_cfg:dict, enemies_cfg:dict,
                         player_speed:float, delta_time:float):
    """Formaciones y espia: solo en alerta AMARILLA o ROJA"""
    if current_condition(world) not in ("YELLOW", "RED"):
        return
    if world.component_for_entity(player_entity, CPlayerState).state != PlayerState.ALIVE:
        return

    c_ts:CTimedSpawner
    for _, c_ts in world.get_component(CTimedSpawner):
        busy = (c_ts.kind == "formation" and world.get_component(CFormationGroup)) or \
               (c_ts.kind == "spy" and world.get_component(CSpy))
        if busy:
            continue
        c_ts.timer += delta_time
        if c_ts.timer < c_ts.interval:
            continue
        c_ts.timer = 0.0
        if random.random() > c_ts.chance:
            continue
        if c_ts.kind == "formation":
            create_formation(world, player_entity, formations_cfg, enemies_cfg, player_speed)
        elif c_ts.kind == "spy":
            create_spy(world, player_entity, camera, spy_cfg, player_speed)
            ServiceLocator.sounds_service.play_cfg(spy_cfg.get("appear_sound"))