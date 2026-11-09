import random
import esper

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_surface import CSurface

def system_blink(world:esper.World, delta_time:float):
    components = world.get_components(CSurface, CBlink)

    c_s:CSurface
    c_b:CBlink
    for _, (c_s, c_b) in components:
        c_b.time -= delta_time
        if c_b.time <= 0:
            c_b.time += random.uniform(c_b.interval_min, c_b.interval_max)
            c_b.visible = not c_b.visible
            c_s.surf = c_b.on_surf if c_b.visible else c_b.off_surf