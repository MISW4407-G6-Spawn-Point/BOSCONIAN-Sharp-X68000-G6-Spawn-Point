import esper
import pygame

from src.ecs.components.c_radar_dot import CRadarDot
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform


def system_radar(world:esper.World, radar_cfg:dict, world_size:dict):
    """Ubica cada punto del radar escalando la posicion de su entidad en el mundo. Si la entidad ya no existe, el punto se elimina"""
    radar_pos = pygame.Vector2(radar_cfg["position"]["x"], radar_cfg["position"]["y"])
    scale = pygame.Vector2(radar_cfg["size"]["w"] / world_size["w"],
                           radar_cfg["size"]["h"] / world_size["h"])

    c_t:CTransform
    c_s:CSurface
    c_r:CRadarDot
    for entity, (c_t, c_s, c_r) in world.get_components(CTransform, CSurface, CRadarDot):
        if not world.entity_exists(c_r.target):
            world.delete_entity(entity)
            continue
        t_t = world.component_for_entity(c_r.target, CTransform)
        t_s = world.component_for_entity(c_r.target, CSurface)
        center = t_t.pos + pygame.Vector2(t_s.area.size) / 2
        dot_center = radar_pos + pygame.Vector2(center.x * scale.x, center.y * scale.y)
        c_t.pos = pygame.Vector2(int(dot_center.x - c_s.area.w / 2),
                                 int(dot_center.y - c_s.area.h / 2))