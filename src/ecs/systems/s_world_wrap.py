import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_world import CTagWorld


def system_world_wrap(world:esper.World, world_w:float, world_h:float):
    """Wraparound: si algo sale por un lado del mundo, aparece por el otro"""
    c_t:CTransform
    for _, (c_t, _) in world.get_components(CTransform, CTagWorld):
        c_t.pos.x %= world_w
        c_t.pos.y %= world_h