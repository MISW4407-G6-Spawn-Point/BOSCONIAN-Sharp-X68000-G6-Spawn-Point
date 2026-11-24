import esper
import pygame

from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_enemy_state import CEnemyState
from src.ecs.components.c_formation_leader import CFormationLeader
from src.ecs.components.c_formation_member import CFormationMember
from src.ecs.components.c_launched_by import CLaunchedBy
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_collision_enemy_obstacle import ENEMY_TYPES, hit_rect
from src.ecs.systems.s_enemy_state import update_enemy_sprite, wrapped_overlap


def _mover(world:esper.World, entity:int) -> int:
    """Quien se mueve: un miembro de formacion activa lo mueve su lider"""
    c_m = world.try_component(entity, CFormationMember)
    if c_m is not None and not c_m.fleeing and world.entity_exists(c_m.leader):
        return c_m.leader
    return entity


def _steering(world:esper.World, entity:int):
    """Componente que guarda el heading de la nave"""
    for component_type in (CEnemyState, CFormationLeader, CFormationMember, CSpy):
        component = world.try_component(entity, component_type)
        if component is not None:
            return component
    return None


def _bounce(world:esper.World, entity:int, push:pygame.Vector2):
    """Saca la nave del choque y refleja su direccion si iba hacia el obstaculo"""
    c_t = world.component_for_entity(entity, CTransform)
    c_t.pos += push
    steering = _steering(world, entity)
    if steering is None or push.length_squared() == 0:
        return
    normal = push.normalize()
    if steering.heading.dot(normal) < 0:
        steering.heading = steering.heading.reflect(normal)
    c_v = world.component_for_entity(entity, CVelocity)
    c_v.vel = steering.heading * c_v.vel.length()
    if isinstance(steering, CEnemyState):
        update_enemy_sprite(c_t, world.component_for_entity(entity, CSurface), steering)


def system_collision_enemy_bounce(world:esper.World, world_size:dict):
    """Enemigos rebotan entre si y contra las bases (ojo y nodos vivos); nadie muere"""
    enemies = [entity for entity, c_lo in world.get_component(CLevelObject)
               if c_lo.object_type in ENEMY_TYPES and world.entity_exists(entity)]

    for i, a in enumerate(enemies):
        for b in enemies[i + 1:]:
            mover_a, mover_b = _mover(world, a), _mover(world, b)
            if mover_a == mover_b:
                continue  # misma formacion: mantiene la figura
            push = wrapped_overlap(hit_rect(world, a), hit_rect(world, b), world_size)
            if push is None:
                continue
            _bounce(world, mover_a, push / 2)
            _bounce(world, mover_b, -push / 2)

    bases = list(world.get_components(CEnemyBaseCombat, CTransform))
    for enemy in enemies:
        launched = world.try_component(enemy, CLaunchedBy)
        for base, (combat, c_t) in bases:
            enemy_rect = hit_rect(world, enemy)
            if launched is not None and launched.base_entity == base:
                base_rect = pygame.Rect(c_t.pos, combat.get_size())
                if wrapped_overlap(enemy_rect, base_rect, world_size) is None:
                    world.remove_component(enemy, CLaunchedBy)
                continue
            rects = [combat.get_eye_rect(c_t.pos)]
            rects += [combat.get_node_rect(c_t.pos, index)
                      for index in range(len(combat.node_centers))
                      if not combat.node_destroyed[index]]
            for rect in rects:
                push = wrapped_overlap(enemy_rect, rect, world_size)
                if push is not None:
                    _bounce(world, _mover(world, enemy), push)
                    break
