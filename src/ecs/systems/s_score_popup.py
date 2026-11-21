import esper

from src.ecs.components.c_score_popup import CScorePopup


def system_score_popup(world:esper.World, delta_time:float):
    for entity, c_p in world.get_component(CScorePopup):
        c_p.remaining -= delta_time
        if c_p.remaining <= 0:
            world.delete_entity(entity)