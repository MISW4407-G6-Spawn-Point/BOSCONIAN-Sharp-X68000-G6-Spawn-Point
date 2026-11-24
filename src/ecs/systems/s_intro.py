import esper

from src.create.prefab_creator import create_intro_step
from src.ecs.components.c_intro_timeline import CIntroTimeline


def system_intro(world: esper.World, delta_time: float):
    """Crea las entidades de cada paso cuando llega su start_time"""
    for _, timeline in world.get_component(CIntroTimeline):
        timeline.time += delta_time
        while timeline.next_step < len(timeline.steps) and \
                timeline.steps[timeline.next_step]["start_time"] <= timeline.time:
            create_intro_step(world, timeline.steps[timeline.next_step], timeline.named)
            timeline.next_step += 1
