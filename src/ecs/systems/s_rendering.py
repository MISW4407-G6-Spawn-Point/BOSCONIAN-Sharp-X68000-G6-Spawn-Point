
import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_hide_on_pause import CTagHideOnPause
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.ecs.components.tags.c_tag_world import CTagWorld
from src.ecs.systems.s_camera import world_to_screen


def system_rendering(world:esper.World, screen:pygame.Surface, camera:CCamera = None,
                     paused:bool = False):
    for entity, (c_t, c_s) in world.get_components(CTransform, CSurface):
        if not world.has_component(entity, CTagUI) and not world.has_component(entity, CTagWorld):
            screen.blit(c_s.surf, c_t.pos, area=c_s.area)

    if camera is not None and not paused:
        screen.set_clip(camera.view)
        for _, (c_t, c_s, _) in world.get_components(CTransform, CSurface, CTagWorld):
            screen.blit(c_s.surf, world_to_screen(camera, c_t.pos), area=c_s.area)
        screen.set_clip(None)

    ui = sorted(world.get_components(CTransform, CSurface, CTagUI),
                key=lambda item: item[1][2].layer)
    for entity, (c_t, c_s, _) in ui:
        if paused and world.has_component(entity, CTagHideOnPause):
            continue
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)