import esper

from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.tags.c_tag_hi_score import CTagHiScore


def system_hi_score(world:esper.World) -> int:
    """Si el puntaje (1UP) supera el HI-SCORE, este se actualiza al mismo tiempo devuelve el puntaje act"""
    score = 0
    for _, c_sd in world.get_component(CScoreDisplay):
        if c_sd.tracks_score:
            score = c_sd.value
    for _, (c_sd, _) in world.get_components(CScoreDisplay, CTagHiScore):
        c_sd.value = max(c_sd.value, score)
    return score