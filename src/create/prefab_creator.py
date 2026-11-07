import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.engine.service_locator import ServiceLocator


def _color(c:dict) -> pygame.Color:
    return pygame.Color(c["r"], c["g"], c["b"], c.get("a", 255))


def create_sprite(world:esper.World, pos:pygame.Vector2, vel:pygame.Vector2,
                  surface:pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity


def create_text(world:esper.World, text:str, font_path:str, size:int, color:dict,
                pos:dict, centered:bool = True, layer:int = 0) -> int:
    """Crea una entidad de texto estatico usando el ServiceLocator para la fuente."""
    font = ServiceLocator.fonts_service.get(font_path, size)
    c_surface = CSurface.from_text(text, font, _color(color))
    position = pygame.Vector2(pos["x"], pos["y"])
    if centered:
        position -= pygame.Vector2(c_surface.area.size) / 2
    text_entity = world.create_entity()
    world.add_component(text_entity, c_surface)
    world.add_component(text_entity, CTransform(position))
    world.add_component(text_entity, CTagUI(layer))
    return text_entity


def create_input_title(world:esper.World):
    input_start = world.create_entity()
    world.add_component(input_start,
                        CInputCommand("START_GAME", pygame.K_RETURN))


def create_input_play(world:esper.World):
    """Controles de Bosconian: flechas, Z disparo, X especial, P pausa, ESC titulo."""
    commands = [
        ("PLAYER_LEFT", pygame.K_LEFT),
        ("PLAYER_RIGHT", pygame.K_RIGHT),
        ("PLAYER_UP", pygame.K_UP),
        ("PLAYER_DOWN", pygame.K_DOWN),
        ("PLAYER_FIRE", pygame.K_z),
        ("PLAYER_SPECIAL", pygame.K_x),
        ("PAUSE", pygame.K_p),
        ("BACK_TO_TITLE", pygame.K_ESCAPE),
    ]
    for name, key in commands:
        input_entity = world.create_entity()
        world.add_component(input_entity, CInputCommand(name, key))