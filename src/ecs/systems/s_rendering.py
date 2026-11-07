
import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_ui import CTagUI

def system_rendering(world:esper.World, screen:pygame.Surface,
                     offset:pygame.Vector2 = pygame.Vector2(0, 0)):
    # 1. Mundo del juego (afectado por el temblor de pantalla)
    for entity, (c_t, c_s) in world.get_components(CTransform, CSurface):
        if not world.has_component(entity, CTagUI):
            screen.blit(c_s.surf, c_t.pos + offset, area=c_s.area)

    # 2. Interfaz encima, ordenada por capa, sin temblor
    ui = sorted(world.get_components(CTransform, CSurface, CTagUI),
                key=lambda item: item[1][2].layer)
    for _, (c_t, c_s, _) in ui:
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)
