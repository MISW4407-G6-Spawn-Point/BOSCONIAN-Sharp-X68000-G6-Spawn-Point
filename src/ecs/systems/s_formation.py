import math
import esper
import pygame

from src.create.prefab_creator import create_score_popup
from src.ecs.components.c_formation_group import CFormationGroup
from src.ecs.components.c_formation_leader import CFormationLeader
from src.ecs.components.c_formation_member import CFormationMember
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_enemy_state import shortest_delta


def system_formation(world:esper.World, player_entity:int, world_size:dict,
                     spacing:float, despawn_distance:float, delta_time:float):
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    c_t:CTransform
    c_v:CVelocity
    c_s:CSurface
    for _, (c_t, c_v, c_s, c_l) in world.get_components(CTransform, CVelocity, CSurface,
                                                         CFormationLeader):
        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        desired = shortest_delta(center, player_center, world_size)
        if desired.length_squared() > 0:
            angle = (c_l.heading.angle_to(desired) + 180) % 360 - 180
            max_turn = c_l.turn_rate * delta_time
            c_l.heading = c_l.heading.rotate(max(-max_turn, min(max_turn, angle)))
        c_v.vel = c_l.heading * c_l.speed
        _set_sprite(c_t, c_s, c_l, c_l.heading)

    for entity, (c_t, c_v, c_s, c_m) in world.get_components(CTransform, CVelocity, CSurface,
                                                             CFormationMember):
        if not world.entity_exists(entity):
            continue
        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        if not c_m.fleeing and world.entity_exists(c_m.leader):
            l_t = world.component_for_entity(c_m.leader, CTransform)
            l_s = world.component_for_entity(c_m.leader, CSurface)
            l_l = world.component_for_entity(c_m.leader, CFormationLeader)
            leader_center = l_t.pos + pygame.Vector2(l_s.area.size) / 2
            rotation = pygame.Vector2(0, -1).angle_to(l_l.heading)
            target = leader_center + (c_m.offset * spacing).rotate(rotation)
            c_m.heading = l_l.heading
            c_v.vel = l_l.heading * l_l.speed
            _set_sprite(c_t, c_s, c_m, c_m.heading)
            c_t.pos = target - pygame.Vector2(c_s.area.size) / 2
            continue

        if not c_m.fleeing:
            c_m.fleeing = True
            away = shortest_delta(player_center, center, world_size)
            c_m.heading = away.normalize() if away.length_squared() > 0 else c_m.heading
        c_v.vel = c_m.heading * c_m.flee_speed
        _set_sprite(c_t, c_s, c_m, c_m.heading)
        if shortest_delta(center, player_center, world_size).length() > despawn_distance:
            for _, group in world.get_component(CFormationGroup):
                if entity in group.members:
                    group.escaped = True
            world.delete_entity(entity)

    c_g:CFormationGroup
    for group_entity, c_g in world.get_component(CFormationGroup):
        alive = [m for m in c_g.members if world.entity_exists(m)]
        if alive:
            m_t = world.component_for_entity(alive[0], CTransform)
            c_g.last_center = m_t.pos.copy()
            continue
        if not c_g.escaped:
            for _, score_display in world.get_component(CScoreDisplay):
                if score_display.tracks_score:
                    score_display.value += c_g.bonus
            create_score_popup(world, c_g.last_center, c_g.bonus)
        world.delete_entity(group_entity)


def _set_sprite(c_t:CTransform, c_s:CSurface, ship, heading:pygame.Vector2):
    """Uno de los 8 sprites pre-rotados segun la direccion (igual que la nave)."""
    angle = math.degrees(math.atan2(heading.x, -heading.y)) % 360
    new_index = round(angle / 45) % 8
    if new_index == ship.dir_index:
        return
    center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
    ship.dir_index = new_index
    c_s.surf = ship.sprites[new_index]
    c_s.area = c_s.surf.get_rect()
    c_t.pos = center - pygame.Vector2(c_s.area.size) / 2