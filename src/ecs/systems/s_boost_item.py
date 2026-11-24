import random

import esper
import pygame

from src.create.prefab_creator import create_boost_item, create_radar_dot
from src.ecs.components.c_boost_item_spawner import CBoostItemSpawner
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_special_power import CSpecialPower
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_boost_item import CTagBoostItem
from src.ecs.systems.s_collision_enemy_obstacle import hit_rect
from src.ecs.systems.s_enemy_state import wrapped_overlap
from src.engine.service_locator import ServiceLocator


def _spawn(world: esper.World, player_entity: int, item_cfg: dict, world_size: dict,
           radar_cfg: dict):
    """Capsula a una distancia al azar del jugador (con wraparound)"""
    player_pos = world.component_for_entity(player_entity, CTransform).pos
    distance = random.uniform(item_cfg["spawn_distance"]["min"],
                              item_cfg["spawn_distance"]["max"])
    pos = player_pos + pygame.Vector2(distance, 0).rotate(random.uniform(0, 360))
    pos.x %= world_size["w"]
    pos.y %= world_size["h"]
    item = create_boost_item(world, pos, item_cfg)
    create_radar_dot(world, item, radar_cfg["dot_size"], item_cfg["radar_color"])


def system_boost_item(world: esper.World, player_entity: int, special_cfg: dict,
                      world_size: dict, radar_cfg: dict, delta_time: float):
    """Genera la capsula (una a la vez) y la recoge al tocarla: +1 carga"""
    item_cfg = special_cfg["item"]
    items = world.get_component(CTagBoostItem)

    for _, spawner in world.get_component(CBoostItemSpawner):
        if items:
            continue
        spawner.timer += delta_time
        if spawner.timer < spawner.interval:
            continue
        spawner.timer = 0.0
        if random.random() < spawner.chance:
            _spawn(world, player_entity, item_cfg, world_size, radar_cfg)

    if world.component_for_entity(player_entity, CPlayerState).state != PlayerState.ALIVE:
        return
    player_rect = hit_rect(world, player_entity)
    c_sp = world.component_for_entity(player_entity, CSpecialPower)
    for item, _ in items:
        c_t = world.component_for_entity(item, CTransform)
        c_s = world.component_for_entity(item, CSurface)
        if wrapped_overlap(player_rect, pygame.Rect(c_t.pos, c_s.area.size), world_size) is None:
            continue
        c_sp.charges = min(c_sp.max_charges, c_sp.charges + 1)
        ServiceLocator.sounds_service.play_cfg(item_cfg.get("pickup_sound"))
        world.delete_entity(item)
