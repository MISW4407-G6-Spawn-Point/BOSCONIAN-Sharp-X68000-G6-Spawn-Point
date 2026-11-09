from typing import Callable
import esper

from src.ecs.components.c_scene_timer import CSceneTimer


def system_scene_timer(world:esper.World, delta_time:float, do_switch:Callable[[str], None]):
    components = world.get_component(CSceneTimer)

    c_st:CSceneTimer
    for _, c_st in components:
        c_st.time -= delta_time
        if c_st.time <= 0:
            do_switch(c_st.next_scene)
            c_st.time = float("inf")  # evita pedir el cambio mas de una vez