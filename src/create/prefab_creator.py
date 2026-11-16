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
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_enemy_base_eye import CEnemyBaseEye
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_explosion import CExplosion
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_sprite_animation import CSpriteAnimation
from src.ecs.components.tags.c_tag_hide_on_pause import CTagHideOnPause
from src.ecs.components.tags.c_tag_pause import CTagPause
from src.create.enemy_base_composer import enemy_base_composer

_LEVEL_SPRITE_AREAS = {
    "enemy_base": {"x": 120, "y": 55, "w": 79, "h": 66},
    "1-a": {"x": 149, "y": 9, "w": 15, "h": 11},
    "1-b": {"x": 166, "y": 6, "w": 14, "h": 14},
    "1-c": {"x": 181, "y": 8, "w": 14, "h": 12},
    "2-a": {"x": 149, "y": 34, "w": 15, "h": 11},
    "2-b": {"x": 167, "y": 31, "w": 14, "h": 14},
    "2-c": {"x": 182, "y": 33, "w": 14, "h": 12},
    "mine": {"x": 2, "y": 89, "w": 11, "h": 11},
    "i": {"x": 0, "y": 111, "w": 14, "h": 14},
    "p": {"x": 20, "y": 113, "w": 13, "h": 12},
    "e": {"x": 41, "y": 109, "w": 7, "h": 16},
}


def _color(c:dict) -> pygame.Color:
    return pygame.Color(c["r"], c["g"], c["b"], c.get("a", 255))


def create_sprite(world:esper.World, pos:pygame.Vector2, vel:pygame.Vector2,
                surface:pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity


def create_enemy_base_surface(
    enemy_base_cfg:dict,
    core_sprite:pygame.Surface,
    module_sprites:list[pygame.Surface],
) -> pygame.Surface:
    if len(module_sprites) != 6:
        raise ValueError("module_sprites debe contener exactamente seis sprites")

    sprite_sheet = ServiceLocator.images_service.get(enemy_base_cfg["image"])
    left_support = _create_level_surface(
        enemy_base_cfg["image"],
        {"x": 90, "y": 0, "w": 13, "h": 42},
    )
    right_support = pygame.transform.flip(left_support, True, False)
    left_connector = _create_level_surface(
        enemy_base_cfg["image"],
        {"x": 98, "y": 19, "w": 8, "h": 4},
    )
    right_connector = pygame.transform.flip(left_connector, True, False)
    eye_sprite = core_sprite
    return enemy_base_composer(
        left_support,
        right_support,
        left_connector,
        right_connector,
        eye_sprite,
        *module_sprites,
        destination_size=enemy_base_cfg.get("size") or (99, 80),
    )


def _create_level_surface(image_path:str, sprite_area:dict) -> pygame.Surface:
    sprite_sheet = ServiceLocator.images_service.get(image_path)
    surface = sprite_sheet.subsurface(pygame.Rect(
        sprite_area["x"],
        sprite_area["y"],
        sprite_area["w"],
        sprite_area["h"],
    )).copy()
    surface.set_colorkey((255, 0, 255))
    return surface


def _create_level_object(
    world:esper.World,
    object_cfg:dict,
    object_type:str,
    score:int,
    node_score:int = 0,
) -> int:
    sprite_area = object_cfg.get("sprite_area", _LEVEL_SPRITE_AREAS[object_type])
    surface = _create_level_surface(object_cfg["image"], sprite_area)
    position = pygame.Vector2(
        object_cfg["position"]["x"],
        object_cfg["position"]["y"],
    )
    entity = create_sprite(world, position, pygame.Vector2(0, 0), surface)
    world.add_component(entity, CTagWorld())
    world.add_component(entity, CLevelObject(object_type, score, node_score))
    return entity


def _create_mine_object(world: esper.World, object_cfg: dict) -> int:
    first_frame = _create_level_surface(
        object_cfg["image"],
        object_cfg.get("full_sprite_area", {"x": 0, "y": 87, "w": 16, "h": 15}),
    )
    second_frame = _create_level_surface(
        object_cfg["image"],
        object_cfg.get(
            "alternate_sprite_area",
            {"x": 19, "y": 87, "w": 16, "h": 15},
        ),
    )
    frames = []
    for frame in (first_frame, second_frame):
        frame.set_colorkey((255, 0, 255))
        frames.append(frame)

    entity = create_sprite(
        world,
        pygame.Vector2(object_cfg["position"]["x"], object_cfg["position"]["y"]),
        pygame.Vector2(0, 0),
        frames[0],
    )
    world.add_component(entity, CTagWorld())
    world.add_component(entity, CLevelObject(
        "mine",
        object_cfg["score"],
    ))
    world.add_component(entity, CSpriteAnimation(frames))
    return entity


def _create_enemy_base_object(
    world: esper.World,
    enemy_base_cfg: dict,
) -> int:
    sprite_sheet = ServiceLocator.images_service.get(enemy_base_cfg["image"])
    left_support = sprite_sheet.subsurface(pygame.Rect(90, 0, 13, 42)).copy()
    left_support.set_colorkey((255, 0, 255))
    right_support = pygame.transform.flip(left_support, True, False)
    left_connector = sprite_sheet.subsurface(pygame.Rect(98, 19, 8, 4)).copy()
    left_connector.set_colorkey((255, 0, 255))
    right_connector = pygame.transform.flip(left_connector, True, False)
    base_surface = pygame.Surface((99, 80), pygame.SRCALPHA)
    eye_frames = []
    for frame_index in range(4):
        frame_area = pygame.Rect(frame_index * 24, 46, 20, 20)
        eye_frame = sprite_sheet.subsurface(frame_area).copy()
        eye_frame.set_colorkey((255, 0, 255))
        eye_frames.append(eye_frame)

    entity = create_sprite(
        world,
        pygame.Vector2(enemy_base_cfg["position"]["x"],
                       enemy_base_cfg["position"]["y"]) - pygame.Vector2(49, 40),
        pygame.Vector2(0, 0),
        base_surface,
    )
    world.add_component(entity, CTagWorld())
    world.add_component(entity, CLevelObject(
        "enemy_base",
        enemy_base_cfg["base_score"],
        enemy_base_cfg["node_score"],
    ))

    node_frames = []
    for frame_index in range(4):
        frame = _create_level_surface(
            enemy_base_cfg["image"],
            {"x": frame_index * 21, "y": 9, "w": 16, "h": 16},
        )
        node_frames.append([frame] * 6)
    combat = CEnemyBaseCombat(
        (left_support, right_support),
        (left_connector, right_connector),
        eye_frames,
        node_frames,
    )
    animated_surface = combat.compose()
    world.component_for_entity(entity, CSurface).surf = animated_surface
    world.add_component(entity, CEnemyBaseEye(animated_surface, eye_frames))
    world.add_component(entity, combat)
    return entity


def create_level_objects(world:esper.World, level_cfg:dict) -> list[int]:
    """Crea las bases y enemigos configurados en el nivel seleccionado."""
    created_entities = []
    enemy_base_configs = level_cfg["enemy_bases"]
    if isinstance(enemy_base_configs, dict):
        enemy_base_configs = [enemy_base_configs]

    occupied_rectangles = []
    for enemy_base_cfg in enemy_base_configs:
        enemy_base_cfg = dict(enemy_base_cfg)
        enemy_base_cfg.setdefault("sprite_area", _LEVEL_SPRITE_AREAS["enemy_base"])
        created_entities.append(_create_enemy_base_object(world, enemy_base_cfg))
        occupied_rectangles.append(pygame.Rect(
            enemy_base_cfg["position"]["x"] - 49,
            enemy_base_cfg["position"]["y"] - 40,
            99,
            80,
        ))
    for enemy_cfg in level_cfg["enemies"]:
        sprite_area = enemy_cfg.get(
            "sprite_area",
            _LEVEL_SPRITE_AREAS[enemy_cfg["type"]],
        )
        enemy_surface = _create_level_surface(enemy_cfg["image"], sprite_area)
        enemy_rect = pygame.Rect(
            enemy_cfg["position"]["x"],
            enemy_cfg["position"]["y"],
            enemy_surface.get_width(),
            enemy_surface.get_height(),
        )
        if any(enemy_rect.colliderect(occupied) for occupied in occupied_rectangles):
            raise ValueError(
                f"El enemigo {enemy_cfg['type']} se solapa con otro elemento"
            )
        occupied_rectangles.append(enemy_rect)
        if enemy_cfg["type"] == "mine":
            created_entities.append(_create_mine_object(world, enemy_cfg))
        else:
            created_entities.append(_create_level_object(
                world,
                enemy_cfg,
                enemy_cfg["type"],
                enemy_cfg["score"],
            ))

    return created_entities


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


def create_explosion(world: esper.World,center: pygame.Vector2,explosion_cfg: dict) -> int:
    frames = []
    for frame_area in explosion_cfg["frames"]:
        frames.append(_create_level_surface(explosion_cfg["image"], frame_area))

    first_frame = frames[0]
    position = center - pygame.Vector2(first_frame.get_size()) / 2
    entity = create_sprite(world, position, pygame.Vector2(0, 0), first_frame)
    world.add_component(entity, CExplosion(frames, explosion_cfg["frame_duration"]))
    world.add_component(entity, CTagWorld())
    ServiceLocator.sounds_service.play(explosion_cfg["sound"])
    return entity


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


def create_hud(
    world:esper.World,
    hud_cfg:dict,
    font_path:str,
    condition_cfg:dict = None,
    initial_score: int = 0,
    round_number: int = 1,
) -> None:
    """Panel derecho: record, puntaje, condicion, radar, vidas y ronda."""
    score_entity = None
    round_entity = None
    for index, text_cfg in enumerate(hud_cfg["texts"]):
        created_text_entity = create_text(
            world,
            text_cfg["text"],
            font_path,
            text_cfg["size"],
            text_cfg["color"],
            text_cfg["position"],
            text_cfg.get("align", "center"),
        )
        if index == 3:
            score_entity = created_text_entity
        elif index == 6:
            round_entity = created_text_entity

    bar = hud_cfg["condition_bar"]
    bar_entity = create_rect(world, bar["position"], bar["size"], bar["color"])
    text_pos = {"x": bar["position"]["x"] + bar["size"]["w"] / 2,
                "y": bar["position"]["y"] + bar["size"]["h"] / 2}
    condition_text_entity = create_text(
        world,
        bar["text"],
        font_path,
        bar["text_size"],
        bar["text_color"],
        text_pos,
        layer=2,
    )
    score_cfg = hud_cfg["texts"][3]
    score_display = CScoreDisplay(
        score_cfg["position"]["x"],
        score_cfg["position"]["y"] + score_cfg["size"] / 2,
        font_path,
        score_cfg["size"],
        _color(score_cfg["color"]),
        initial_score,
    )
    world.add_component(score_entity, score_display)
    round_cfg = hud_cfg["texts"][6]
    world.add_component(round_entity, CScoreDisplay(
        round_cfg["position"]["x"],
        round_cfg["position"]["y"] + round_cfg["size"] / 2,
        font_path,
        round_cfg["size"],
        _color(round_cfg["color"]),
        round_number,
        tracks_score=False,
    ))
    text_surface = world.component_for_entity(condition_text_entity, CSurface)
    text_transform = world.component_for_entity(condition_text_entity, CTransform)
    text_transform.pos = pygame.Vector2(
        text_pos["x"],
        text_pos["y"],
    ) - pygame.Vector2(text_surface.surf.get_size()) / 2
    if condition_cfg is not None:
        world.add_component(condition_text_entity, CConditionDisplay(
            bar_entity,
            condition_text_entity,
            condition_cfg["yellow"],
            condition_cfg["red"],
            font_path,
            bar["text_size"],
            _color(bar["text_color"]),
            pygame.Vector2(text_pos["x"], text_pos["y"]),
        ))

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