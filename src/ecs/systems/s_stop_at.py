import esper
import pygame

from src.ecs.components.c_stop_at import CStopAt
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


def system_stop_at(world: esper.World):
    """Frena en seco la entidad cuando cruza su y de destino"""
    for entity, (c_t, c_v, c_st) in world.get_components(CTransform, CVelocity, CStopAt):
        if (c_v.vel.y < 0 and c_t.pos.y <= c_st.y) or (c_v.vel.y > 0 and c_t.pos.y >= c_st.y):
            c_t.pos.y = c_st.y
            c_v.vel = pygame.Vector2(0, 0)
            world.remove_component(entity, CStopAt)
