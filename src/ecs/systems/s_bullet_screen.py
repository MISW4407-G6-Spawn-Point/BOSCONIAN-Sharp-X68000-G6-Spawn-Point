import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.systems.s_camera import world_to_screen


def system_bullet_screen(world:esper.World, camera:CCamera):
    """Elimina las balas que salen del area visible de la camara"""
    c_t:CTransform
    c_s:CSurface
    for entity, (c_t, c_s, _) in world.get_components(CTransform, CSurface, CTagBullet):
        screen_rect = pygame.Rect(world_to_screen(camera, c_t.pos), c_s.area.size)
        if not camera.view.colliderect(screen_rect):
            world.delete_entity(entity)