import esper

from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_special_power import CSpecialPower
from src.ecs.components.tags.c_tag_special_display import CTagSpecialDisplay


def system_special_hud(world: esper.World, player_entity: int):
    """Copia las cargas del BOOST al numero del HUD."""
    c_sp = world.component_for_entity(player_entity, CSpecialPower)
    for _, (c_sd, _) in world.get_components(CScoreDisplay, CTagSpecialDisplay):
        c_sd.value = c_sp.charges