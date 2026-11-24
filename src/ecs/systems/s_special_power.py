import esper
import pygame

from src.create.prefab_creator import create_boost_trail
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_special_power import CSpecialPower
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def activate_boost(world: esper.World, player_entity: int, special_cfg: dict) -> bool:
    """X: gasta una carga y sube la velocidad maxima (no destruye nada)"""
    c_sp = world.component_for_entity(player_entity, CSpecialPower)
    if c_sp.charges <= 0 or c_sp.time_left > 0 or c_sp.cooldown_left > 0:
        return False
    c_sp.charges -= 1
    c_sp.time_left = special_cfg["duration"]
    c_p = world.component_for_entity(player_entity, CPlayerShip)
    c_p.max_speed = c_sp.normal_speed * special_cfg["speed_multiplier"]
    c_p.speed = c_p.max_speed
    ServiceLocator.sounds_service.play_cfg(special_cfg.get("sound"))
    return True


def _end_boost(c_sp: CSpecialPower, c_p: CPlayerShip, cooldown: float):
    c_sp.time_left = 0.0
    c_sp.cooldown_left = cooldown
    c_p.max_speed = c_sp.normal_speed


def system_special_power(world: esper.World, player_entity: int, special_cfg: dict,
                         delta_time: float):
    """Temporizadores del BOOST y estela mientras esta activo"""
    c_sp = world.component_for_entity(player_entity, CSpecialPower)
    c_p = world.component_for_entity(player_entity, CPlayerShip)
    c_sp.cooldown_left = max(0.0, c_sp.cooldown_left - delta_time)
    if c_sp.time_left <= 0:
        return
    if world.component_for_entity(player_entity, CPlayerState).state != PlayerState.ALIVE:
        _end_boost(c_sp, c_p, special_cfg["cooldown"])
        return
    c_sp.time_left -= delta_time
    if c_sp.time_left <= 0:
        _end_boost(c_sp, c_p, special_cfg["cooldown"])
        return

    trail = special_cfg["trail"]
    c_sp.trail_timer -= delta_time
    if c_sp.trail_timer <= 0:
        c_sp.trail_timer = trail["interval"]
        c_t = world.component_for_entity(player_entity, CTransform)
        c_s = world.component_for_entity(player_entity, CSurface)
        create_boost_trail(world, c_t.pos + pygame.Vector2(c_s.area.size) / 2, trail)
