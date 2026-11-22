import random
import esper
import pygame

from src.create.prefab_creator import create_enemy
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def current_condition(world:esper.World) -> str:
    """Fase de alerta actual (GREEN, YELLOW o RED)"""
    for _, condition in world.get_component(CConditionDisplay):
        return condition.phase
    return "GREEN"


def system_enemy_spawner(world:esper.World, player_entity:int, enemies_cfg:dict,
                         world_size:dict, player_speed:float, delta_time:float):
    """VERDE (no salen enemigos) | AMARILLA (salen cada 'interval') | ROJA (salen al doble de ritmo y van al doble de velocidad)"""
    phase = current_condition(world)
    if phase not in ("YELLOW", "RED"):
        return
    pl_state = world.component_for_entity(player_entity, CPlayerState)
    if pl_state.state != PlayerState.ALIVE:
        return

    is_red = phase == "RED"
    rate = enemies_cfg["red_rate_multiplier"] if is_red else 1.0
    speed_mult = enemies_cfg["red_speed_multiplier"] if is_red else 1.0

    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    c_sp:CEnemySpawner
    for _, c_sp in world.get_component(CEnemySpawner):
        c_sp.timer += delta_time * rate
        if c_sp.timer < c_sp.interval:
            continue
        c_sp.timer = 0.0
        if len(world.get_component(CTagEnemy)) >= c_sp.max_enemies:
            continue

        types = list(c_sp.weights.keys())
        enemy_type = random.choices(types, weights=[c_sp.weights[t] for t in types])[0]
        offset = pygame.Vector2(enemies_cfg["spawn_distance"], 0).rotate(random.uniform(0, 360))
        pos = player_center + offset
        pos.x %= world_size["w"]
        pos.y %= world_size["h"]
        speed = player_speed * enemies_cfg["types"][enemy_type]["speed_factor"] * speed_mult
        heading = -offset.normalize()  # sale apuntando hacia el jugador
        create_enemy(world, pos, enemy_type, enemies_cfg, heading, speed, c_sp.accuracy)