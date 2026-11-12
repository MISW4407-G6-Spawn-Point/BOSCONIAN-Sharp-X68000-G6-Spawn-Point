import esper

from src.ecs.components.c_star import CStar
from src.ecs.components.c_transform import CTransform


def system_star_wrap(world:esper.World, area:dict):
    """Mantiene las estrellas dentro del area de juego"""
    c_t:CTransform
    for _, (c_t, _) in world.get_components(CTransform, CStar):
        c_t.pos.x = area["x"] + (c_t.pos.x - area["x"]) % area["w"]
        c_t.pos.y = area["y"] + (c_t.pos.y - area["y"]) % area["h"]