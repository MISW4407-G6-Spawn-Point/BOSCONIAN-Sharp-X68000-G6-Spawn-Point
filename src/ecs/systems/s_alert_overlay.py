import esper

from src.create.prefab_creator import create_alert_overlay
from src.ecs.components.c_formation_leader import CFormationLeader
from src.ecs.components.c_spy import CSpy
from src.ecs.components.tags.c_tag_alert_overlay import CTagAlertOverlay


def system_alert_overlay(world:esper.World, alerts_cfg:dict, font_path:str):
    """Mientras hay espia o formacion, tapa CONDITION con su cartel"""
    if world.get_component(CSpy):
        wanted = "spy"
    elif world.get_component(CFormationLeader):
        wanted = "formation"
    else:
        wanted = None

    current = [(entity, tag) for entity, tag in world.get_component(CTagAlertOverlay)]
    if current and current[0][1].kind == wanted:
        return
    for entity, _ in current:
        world.delete_entity(entity)
    if wanted is not None:
        create_alert_overlay(world, alerts_cfg, alerts_cfg[wanted], font_path, wanted)