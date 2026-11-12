import random

import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_scene_timer import CSceneTimer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.engine.service_locator import ServiceLocator
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_star import CStar
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_world import CTagWorld
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.c_radar_dot import CRadarDot
from src.ecs.components.tags.c_tag_hide_on_pause import CTagHideOnPause
from src.ecs.components.tags.c_tag_pause import CTagPause


def _color(c:dict) -> pygame.Color:
    return pygame.Color(c["r"], c["g"], c["b"], c.get("a", 255))


def create_sprite(world:esper.World, pos:pygame.Vector2, vel:pygame.Vector2,
                surface:pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity


def _anchor(position:pygame.Vector2, size:pygame.Vector2, align:str) -> pygame.Vector2:
    """Mueve la posicion de anclaje segun la alineacion (left, center, right)."""
    if align == "center":
        position.x -= size.x / 2
    elif align == "right":
        position.x -= size.x
    return position


def create_text(world:esper.World, text:str, font_path:str, size:int, color:dict,
                pos:dict, align:str = "center", layer:int = 1) -> int:
    """Crea una entidad de texto estatico. En x se alinea segun align; en y, pos es el borde superior."""
    font = ServiceLocator.fonts_service.get(font_path, size)
    c_surface = CSurface.from_text(text, font, _color(color))
    position = _anchor(pygame.Vector2(pos["x"], pos["y"]),
                    pygame.Vector2(c_surface.area.size), align)
    text_entity = world.create_entity()
    world.add_component(text_entity, c_surface)
    world.add_component(text_entity, CTransform(position))
    world.add_component(text_entity, CTagUI(layer))
    return text_entity


def create_texts(world:esper.World, texts:list, font_path:str):
    """Crea una lista de textos descritos en un .json."""
    for info in texts:
        create_text(world, info["text"], font_path, info["size"], info["color"],
                    info["position"], info.get("align", "center"))


def create_rect(world:esper.World, pos:dict, size:dict, color:dict, layer:int = 0) -> int:
    """Rectangulo de color solido (elemento de interfaz)."""
    rect_entity = world.create_entity()
    world.add_component(rect_entity,
                        CSurface(pygame.Vector2(size["w"], size["h"]), _color(color)))
    world.add_component(rect_entity,
                        CTransform(pygame.Vector2(pos["x"], pos["y"])))
    world.add_component(rect_entity, CTagUI(layer))
    return rect_entity


def create_starfield(world:esper.World, world_cfg:dict, area:dict, in_menu:bool) -> None:
    """Fondo de estrellas titilantes de colores dentro del area de juego."""
    colors = world_cfg["star_colors"]
    blink = world_cfg["stars_blink_speed"]
    parallax = world_cfg["stars_parallax"]
    menu_vel = world_cfg["stars_menu_velocity"]
    for _ in range(world_cfg["stars_number"]):
        star_entity = world.create_entity()
        c_surface = CSurface(pygame.Vector2(1, 1), _color(random.choice(colors)))
        pos = pygame.Vector2(random.randint(area["x"], area["x"] + area["w"] - 1),
                            random.randint(area["y"], area["y"] + area["h"] - 1))
        vel = pygame.Vector2(0, random.uniform(menu_vel["min"], menu_vel["max"])) \
            if in_menu else pygame.Vector2(0, 0)
        world.add_component(star_entity, c_surface)
        world.add_component(star_entity, CTransform(pos))
        world.add_component(star_entity, CVelocity(vel))
        world.add_component(star_entity, CStar(random.uniform(parallax["min"], parallax["max"])))
        world.add_component(star_entity,
                            CBlink(c_surface.surf, blink["min"], blink["max"]))


def create_hud(world:esper.World, hud_cfg:dict, font_path:str) -> None:
    """Panel derecho: record, puntaje, condicion, radar, vidas y ronda."""
    create_texts(world, hud_cfg["texts"], font_path)

    bar = hud_cfg["condition_bar"]
    create_rect(world, bar["position"], bar["size"], bar["color"])
    text_pos = {"x": bar["position"]["x"] + bar["size"]["w"] / 2,
                "y": bar["position"]["y"] + (bar["size"]["h"] - bar["text_size"]) / 2}
    create_text(world, bar["text"], font_path, bar["text_size"], bar["text_color"],
                text_pos, layer=2)

    radar = hud_cfg["radar"]
    create_rect(world, radar["position"], radar["size"], radar["color"])

    lives = hud_cfg["lives"]
    sheet = ServiceLocator.images_service.get(lives["image"])
    area = lives["area"]
    icon = sheet.subsurface(pygame.Rect(area["x"], area["y"], area["w"], area["h"]))
    for i in range(lives["count"]):
        life_entity = world.create_entity()
        pos = pygame.Vector2(lives["position"]["x"] + i * (area["w"] + lives["spacing"]),
                        lives["position"]["y"])
        world.add_component(life_entity, CSurface.from_surface(icon))
        world.add_component(life_entity, CTransform(pos))
        world.add_component(life_entity, CTagUI(1))


def create_boot_cursor(world:esper.World, cursor_cfg:dict) -> int:
    """Cursor parpadeante de la pantalla de arranque del X68000."""
    cursor_entity = world.create_entity()
    size = pygame.Vector2(cursor_cfg["size"]["w"], cursor_cfg["size"]["h"])
    c_surface = CSurface(size, _color(cursor_cfg["color"]))
    world.add_component(cursor_entity, c_surface)
    world.add_component(cursor_entity, CTransform(
        pygame.Vector2(cursor_cfg["position"]["x"], cursor_cfg["position"]["y"])))
    world.add_component(cursor_entity, CBlink(c_surface.surf, cursor_cfg["blink_time"]))
    world.add_component(cursor_entity, CTagUI(1))
    return cursor_entity


def create_function_keys(world:esper.World, keys_cfg:dict, font_path:str) -> None:
    """Barra inferior de teclas de funcion (C1, CU, CA...) del X68000."""
    box = keys_cfg["box_size"]
    for i, label in enumerate(keys_cfg["labels"]):
        x = keys_cfg["position"]["x"] + i * keys_cfg["step"] \
            + (i // keys_cfg["group_size"]) * keys_cfg["group_gap"]
        y = keys_cfg["position"]["y"]
        create_rect(world, {"x": x, "y": y}, box, keys_cfg["box_color"])
        text_pos = {"x": x + box["w"] / 2, "y": y + (box["h"] - keys_cfg["text_size"]) / 2}
        create_text(world, label, font_path, keys_cfg["text_size"],
                    keys_cfg["text_color"], text_pos, layer=1)


def create_logo(world:esper.World, logo_cfg:dict) -> int:
    """Logo de la pantalla de titulo, centrado en x."""
    surface = ServiceLocator.images_service.get(logo_cfg["image"])
    c_surface = CSurface.from_surface(surface)
    pos = _anchor(pygame.Vector2(logo_cfg["position"]["x"], logo_cfg["position"]["y"]),
                pygame.Vector2(c_surface.area.size), "center")
    logo_entity = world.create_entity()
    world.add_component(logo_entity, c_surface)
    world.add_component(logo_entity, CTransform(pos))
    world.add_component(logo_entity, CTagUI(1))
    return logo_entity


def create_scene_timer(world:esper.World, scene_cfg:dict) -> int:
    """Temporizador que lleva a la siguiente escena segun scenes.json."""
    timer_entity = world.create_entity()
    world.add_component(timer_entity,
                        CSceneTimer(scene_cfg["duration"], scene_cfg["next_scene"]))
    return timer_entity


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

def create_player_ship(world:esper.World, player_cfg:dict, start_pos:dict) -> int:
    """Nave del jugado, con sus 8 sprites pre-rotados."""
    sheet = ServiceLocator.images_service.get(player_cfg["image"])
    area = player_cfg["area"]
    base = sheet.subsurface(pygame.Rect(area["x"], area["y"], area["w"], area["h"]))
    sprites = [pygame.transform.rotate(base, -45 * i) for i in range(8)]

    start_dir = player_cfg["start_direction"]
    surface = sprites[start_dir]
    pos = pygame.Vector2(start_pos["x"], start_pos["y"]) \
        - pygame.Vector2(surface.get_size()) / 2
    player_entity = create_sprite(world, pos, pygame.Vector2(0, 0), surface)
    world.add_component(player_entity, CTagPlayer())
    world.add_component(player_entity, CTagWorld())
    world.add_component(player_entity, CPlayerShip(sprites, player_cfg["max_speed"],
                                                   player_cfg["acceleration"], start_dir))
    return player_entity


def create_camera(world:esper.World, target:int, play_area:dict, world_size:dict) -> int:
    """Camara que sigue al objetivo; su vista es el area de juego (sin el HUD)."""
    camera_entity = world.create_entity()
    view = pygame.Rect(play_area["x"], play_area["y"], play_area["w"], play_area["h"])
    world.add_component(camera_entity,
                        CCamera(target, view, pygame.Vector2(world_size["w"], world_size["h"])))
    return camera_entity

def _bullet_surface(sheet:pygame.Surface, areas:dict, dir_index:int) -> pygame.Surface:
    """Sprite de bala segun la direccion (0 arriba, sentido horario)."""
    def cut(name:str) -> pygame.Surface:
        a = areas[name]
        return sheet.subsurface(pygame.Rect(a["x"], a["y"], a["w"], a["h"]))
    if dir_index in (0, 4):
        return cut("vertical")
    if dir_index in (2, 6):
        return cut("horizontal")
    if dir_index in (1, 5):
        return cut("diagonal")          # "/"
    return pygame.transform.flip(cut("diagonal"), True, False)  # diagonal invertida


def create_player_bullets(world:esper.World, player_entity:int, bullet_cfg:dict) -> None:
    """Disparo"""
    p_t = world.component_for_entity(player_entity, CTransform)
    p_s = world.component_for_entity(player_entity, CSurface)
    p_ship = world.component_for_entity(player_entity, CPlayerShip)
    center = p_t.pos + pygame.Vector2(p_s.area.size) / 2
    sheet = ServiceLocator.images_service.get(bullet_cfg["image"])

    for dir_index in (p_ship.dir_index, (p_ship.dir_index + 4) % 8):
        direction = pygame.Vector2(0, -1).rotate(45 * dir_index)
        surface = _bullet_surface(sheet, bullet_cfg["areas"], dir_index)
        pos = center - pygame.Vector2(surface.get_size()) / 2
        bullet_entity = create_sprite(world, pos, direction * bullet_cfg["velocity"], surface)
        world.add_component(bullet_entity, CTagBullet())
        world.add_component(bullet_entity, CTagWorld())

    if bullet_cfg.get("sound"):
        ServiceLocator.sounds_service.play(bullet_cfg["sound"])

def create_radar_dot(world:esper.World, target:int, size:dict, color:dict) -> int:
    """Punto del minimapa"""
    dot_entity = world.create_entity()
    world.add_component(dot_entity, CSurface(pygame.Vector2(size["w"], size["h"]), _color(color)))
    world.add_component(dot_entity, CTransform(pygame.Vector2(0, 0)))
    world.add_component(dot_entity, CTagUI(2))
    world.add_component(dot_entity, CRadarDot(target))
    world.add_component(dot_entity, CTagHideOnPause())
    return dot_entity

def create_pause_text(world:esper.World, pause_cfg:dict, font_path:str) -> int:
    """Texto de pausa sobre el area de juego"""
    text_entity = create_text(world, pause_cfg["text"], font_path, pause_cfg["size"],
                              pause_cfg["color"], pause_cfg["position"], layer=3)
    if pause_cfg["blink_time"] > 0:
        c_s = world.component_for_entity(text_entity, CSurface)
        world.add_component(text_entity, CBlink(c_s.surf, pause_cfg["blink_time"]))
    world.add_component(text_entity, CTagPause())
    return text_entity