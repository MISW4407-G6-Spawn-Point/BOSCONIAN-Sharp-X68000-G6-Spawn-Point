import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_life_icon import CTagLifeIcon


def system_lives_hud(world:esper.World, lives:int):
    """Muestra iconos como vidas"""
    c_s:CSurface
    c_li:CTagLifeIcon
    for _, (c_s, c_li) in world.get_components(CSurface, CTagLifeIcon):
        c_s.surf.set_alpha(255 if c_li.index < lives else 0)