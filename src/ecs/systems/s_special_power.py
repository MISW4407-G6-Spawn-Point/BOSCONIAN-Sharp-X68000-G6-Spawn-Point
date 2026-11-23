import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_special_power import CSpecialPower
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_camera import world_to_screen


def system_special_power(world: esper.World, player_entity: int, camera: CCamera,
                        special_cfg: dict, explosion_cfg: dict):
    """Poder especial: destruye todo lo destruible que se ve en pantalla y suma sus puntos.
    Las bases enemigas no se tocan. Gasta un uso."""
    c_sp = world.component_for_entity(player_entity, CSpecialPower)
    if c_sp.uses_left <= 0:
        return
    c_sp.uses_left -= 1

    for entity, (c_lo, c_t, c_s) in world.get_components(CLevelObject, CTransform, CSurface):
        if c_lo.object_type not in special_cfg["targets"]:
            continue
        screen_rect = pygame.Rect(world_to_screen(camera, c_t.pos), c_s.area.size)
        if not camera.view.colliderect(screen_rect):
            continue
        create_explosion(world, c_t.pos + pygame.Vector2(c_s.area.size) / 2, explosion_cfg,
                         world.component_for_entity(entity, CVelocity).vel)
        _add_score(world, c_lo.score)
        world.delete_entity(entity)


def _add_score(world: esper.World, points: int):
    for _, score_display in world.get_component(CScoreDisplay):
        if score_display.tracks_score:
            score_display.value += points