import esper
import pygame

from src.ecs.components.c_star import CStar
from src.ecs.components.c_transform import CTransform


def system_star_parallax(world:esper.World, camera_delta:pygame.Vector2):
    """Las estrellas se desplazan en sentido contrario a la camara, mas lento que el mundo."""
    c_t:CTransform
    c_st:CStar
    for _, (c_t, c_st) in world.get_components(CTransform, CStar):
        c_t.pos -= camera_delta * c_st.parallax