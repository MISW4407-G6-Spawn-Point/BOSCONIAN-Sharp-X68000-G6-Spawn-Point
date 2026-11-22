import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_camera import world_to_screen
from src.ecs.systems.s_enemy_state import shortest_delta
from src.engine.service_locator import ServiceLocator


def system_spy(world:esper.World, player_entity:int, camera:CCamera, world_size:dict,
               escape_sound:str):
    """Rebota la primera vez que toca el borde de la pantalla; la segunda se escapa y la alerta pasa a ROJA"""
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2
    view = camera.view

    c_t:CTransform
    c_v:CVelocity
    c_s:CSurface
    c_sp:CSpy
    for entity, (c_t, c_v, c_s, c_sp, c_lo) in world.get_components(
            CTransform, CVelocity, CSurface, CSpy, CLevelObject):
        rect = pygame.Rect(world_to_screen(camera, c_t.pos), c_s.area.size)
        if not c_sp.bounced:
            if (rect.left < view.left and c_sp.heading.x < 0) or \
               (rect.right > view.right and c_sp.heading.x > 0):
                c_sp.heading.x *= -1
                c_sp.bounced = True
            elif (rect.top < view.top and c_sp.heading.y < 0) or \
                 (rect.bottom > view.bottom and c_sp.heading.y > 0):
                c_sp.heading.y *= -1
                c_sp.bounced = True
        elif not view.colliderect(rect):
            world.delete_entity(entity)
            for _, condition in world.get_component(CConditionDisplay):
                condition.elapsed_time = max(condition.elapsed_time, condition.red_time)
            if escape_sound:
                ServiceLocator.sounds_service.play(escape_sound)
            continue
        c_v.vel = c_sp.heading * c_sp.speed

        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        distance = shortest_delta(center, player_center, world_size).length()
        for step in c_sp.score_steps:
            if distance <= step.get("max_distance", float("inf")):
                c_lo.score = step["score"]
                break