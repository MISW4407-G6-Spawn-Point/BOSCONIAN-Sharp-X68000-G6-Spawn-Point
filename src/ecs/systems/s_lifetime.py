import esper

from src.ecs.components.c_lifetime import CLifetime


def system_lifetime(world:esper.World, delta_time:float):
    for entity, c_l in world.get_component(CLifetime):
        c_l.time_left -= delta_time
        if c_l.time_left <= 0:
            world.delete_entity(entity)
