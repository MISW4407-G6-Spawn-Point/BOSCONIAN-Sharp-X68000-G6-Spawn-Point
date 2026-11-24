import esper

from src.ecs.components.c_scroll import CScroll
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform


def system_scroll(world: esper.World, delta_time: float, top_limit: float) -> bool:
    """Sube las entidades con CScroll; devuelve True cuando todas pasaron top_limit"""
    finished = None
    for _, (c_t, c_s, c_sc) in world.get_components(CTransform, CSurface, CScroll):
        c_t.pos.y -= c_sc.speed * delta_time
        bottom = c_t.pos.y + c_s.area.height
        finished = (finished is not False) and bottom < top_limit
    return bool(finished)
