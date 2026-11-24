import random

import esper
import pygame

from src.create.prefab_creator import (create_enemy, create_enemy_bullet, create_explosion,
                                       create_score_popup)
from src.ecs.components.c_boss import CBoss
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_enemy_base_eye import CEnemyBaseEye
from src.ecs.components.c_launched_by import CLaunchedBy
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_collision_bullet_level_object import explode_base
from src.ecs.systems.s_enemy_state import shortest_delta


def _add_score(world: esper.World, points: int):
    for _, score_display in world.get_component(CScoreDisplay):
        if score_display.tracks_score:
            score_display.value += points


def boss_health(boss: CBoss, combat: CEnemyBaseCombat) -> float:
    """Vida restante (0..1): golpes que le quedan a las torretas mas los del nucleo"""
    node_hits = sum(0 if destroyed else 3 - min(damage, 3)
                    for damage, destroyed in zip(combat.node_damage, combat.node_destroyed))
    total = 3 * len(combat.node_damage) + boss.max_core_hp
    return (node_hits + max(boss.core_hp, 0)) / total


def _update_bar(world: esper.World, boss: CBoss, combat: CEnemyBaseCombat):
    if not world.entity_exists(boss.bar_entity):
        return
    c_s = world.component_for_entity(boss.bar_entity, CSurface)
    c_s.area = pygame.Rect(0, 0, round(boss.bar_width * boss_health(boss, combat)),
                           c_s.surf.get_height())


def _arrive(c_v: CVelocity, to_player: pygame.Vector2, move_cfg: dict, delta_time: float):
    """Steering "arrive": se acerca al jugador y frena al llegar a keep_distance"""
    distance = to_player.length()
    desired = pygame.Vector2(0, 0)
    if distance > move_cfg["keep_distance"]:
        factor = min(1.0, (distance - move_cfg["keep_distance"]) / move_cfg["slow_radius"])
        desired = to_player.normalize() * move_cfg["max_speed"] * factor
    steer = desired - c_v.vel
    max_change = move_cfg["max_force"] * delta_time
    if steer.length() > max_change:
        steer.scale_to_length(max_change)
    c_v.vel += steer


def _open_core(world: esper.World, entity: int, boss: CBoss, combat: CEnemyBaseCombat):
    boss.phase = "core"
    combat.eye_frame_index = world.component_for_entity(entity, CEnemyBaseEye).open_frame
    c_s = world.component_for_entity(entity, CSurface)
    c_s.surf = combat.compose()
    c_s.area = c_s.surf.get_rect()


def _attack(world: esper.World, entity: int, boss: CBoss, core_center: pygame.Vector2,
            to_player: pygame.Vector2, boss_cfg: dict, enemies_cfg: dict,
            enemy_bullet_cfg: dict, player_speed: float, delta_time: float):
    """Fase 2: lanza E por el nucleo y dispara en abanico hacia el jugador"""
    direction = to_player.normalize()
    boss.launch_timer -= delta_time
    if boss.launch_timer <= 0:
        boss.launch_timer = boss_cfg["launch_interval"]
        speed = player_speed * enemies_cfg["types"]["e"]["speed_factor"]
        enemy = create_enemy(world, pygame.Vector2(core_center), "e", enemies_cfg, direction,
                             speed, enemies_cfg["default_spawn"]["accuracy"])
        world.add_component(enemy, CLaunchedBy(entity))
    fan = boss_cfg["fan"]
    boss.fan_timer -= delta_time
    if boss.fan_timer <= 0:
        boss.fan_timer = fan["interval"]
        for i in range(fan["count"]):
            angle = -fan["spread"] / 2 + fan["spread"] * i / max(1, fan["count"] - 1)
            create_enemy_bullet(world, pygame.Vector2(core_center), direction.rotate(angle),
                                enemy_bullet_cfg)


def _die(world: esper.World, entity: int, boss: CBoss, combat: CEnemyBaseCombat,
         c_t: CTransform, boss_cfg: dict, explosion_cfg: dict):
    boss.phase = "dying"
    boss.death_timer = boss_cfg["death"]["time"]
    explode_base(world, c_t.pos, combat, explosion_cfg)
    score = world.component_for_entity(entity, CLevelObject).score
    _add_score(world, score)
    create_score_popup(world, combat.get_core_center(c_t.pos), score)


def _dying(world: esper.World, entity: int, boss: CBoss, c_t: CTransform, c_v: CVelocity,
           c_s: CSurface, boss_cfg: dict, explosion_cfg: dict, delta_time: float):
    """Explosiones repartidas por el cuerpo y al final desaparece"""
    c_v.vel = pygame.Vector2(0, 0)
    boss.death_timer -= delta_time
    boss.explosion_timer -= delta_time
    if boss.explosion_timer <= 0:
        boss.explosion_timer = boss_cfg["death"]["explosion_interval"]
        point = c_t.pos + pygame.Vector2(random.uniform(0, c_s.area.w),
                                         random.uniform(0, c_s.area.h))
        create_explosion(world, point, explosion_cfg)
    if boss.death_timer <= 0:
        world.delete_entity(entity)


def system_boss(world: esper.World, player_entity: int, world_size: dict, boss_cfg: dict,
                enemies_cfg: dict, enemy_bullet_cfg: dict, explosion_cfg: dict,
                player_speed: float, delta_time: float):
    """Movimiento, fases, ataques, barra de vida y muerte del jefe"""
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2
    player_alive = world.component_for_entity(player_entity, CPlayerState).state == \
        PlayerState.ALIVE

    for entity, (boss, combat, c_t, c_v, c_s) in world.get_components(
            CBoss, CEnemyBaseCombat, CTransform, CVelocity, CSurface):
        _update_bar(world, boss, combat)
        if boss.phase == "dying":
            _dying(world, entity, boss, c_t, c_v, c_s, boss_cfg, explosion_cfg, delta_time)
            continue

        core_center = combat.get_core_center(c_t.pos)
        to_player = shortest_delta(core_center, player_center, world_size)
        _arrive(c_v, to_player, boss_cfg["movement"], delta_time)

        if boss.phase == "turrets" and combat.has_been_destroyed():
            _open_core(world, entity, boss, combat)
        if boss.phase != "core":
            continue
        if boss.core_hp <= 0:
            _die(world, entity, boss, combat, c_t, boss_cfg, explosion_cfg)
        elif player_alive and to_player.length_squared() > 0:
            _attack(world, entity, boss, core_center, to_player, boss_cfg, enemies_cfg,
                    enemy_bullet_cfg, player_speed, delta_time)
