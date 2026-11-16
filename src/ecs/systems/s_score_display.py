import esper
import pygame
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def system_score_display(world: esper.World) -> None:
    for entity, (score, surface, transform) in world.get_components(
        CScoreDisplay,
        CSurface,
        CTransform,
    ):
        font = ServiceLocator.fonts_service.get(score.font_path, score.text_size)
        surface.surf = font.render(str(score.value), True, score.text_color)
        surface.area = surface.surf.get_rect()
        transform.pos = pygame.Vector2(
            score.right_x - surface.surf.get_width(),
            score.center_y - surface.surf.get_height() / 2,
        )
