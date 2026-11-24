"""Editor de niveles (F4 en PlayScene): bases, inicio del jugador y opciones de la ronda.
Lo editado es un "override" por ronda que PlayScene aplica sobre level.json"""

import pygame

from src.create.prefab_creator import create_enemy_base, create_sprite, create_text
from src.ecs.components.c_base_core import CBaseCore
from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_editor import CTagEditor
from src.ecs.components.tags.c_tag_world import CTagWorld
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_enemy_state import shortest_delta
from src.ecs.systems.s_radar import system_radar
from src.ecs.systems.s_star_parallax import system_star_parallax
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.service_locator import ServiceLocator

DEFAULT = "DEFAULT"


def original_level_data(level_cfg: dict, player_start: dict) -> dict:
    """Datos editables de una ronda tal como vienen de level.json"""
    return {
        "enemy_bases": [{"position": dict(base["position"]),
                         "orientation": base.get("orientation", "horizontal"),
                         "core_mode": base.get("core_mode", "cycle")}
                        for base in level_cfg.get("enemy_bases", [])],
        "player_start": dict(player_start),
        "special_shot": level_cfg.get("special_shot", False),
        "difficulty": DEFAULT,
        "music": -1,
        "boost_item_chance": level_cfg.get("boost_item_chance", 0.5),
    }


def apply_level_override(level_cfg: dict, override: dict, editor_cfg: dict) -> dict:
    """Config de la ronda con lo editado encima (level.json no se modifica)"""
    result = dict(level_cfg)
    defaults = editor_cfg["base_defaults"]
    result["enemy_bases"] = [dict(defaults, **base) for base in override["enemy_bases"]]
    result["special_shot"] = override["special_shot"]
    result["boost_item_chance"] = override["boost_item_chance"]
    if override["difficulty"] != DEFAULT:
        result["condition"] = dict(editor_cfg["difficulties"][override["difficulty"]])
    result["music"] = override["music"]
    return result


class LevelEditor:
    def __init__(self, scene, original: dict, data: dict) -> None:
        self._scene = scene
        self._world = scene.ecs_world
        self._cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")["editor"]
        self._original = original
        self._options = {key: data[key] for key in
                         ("special_shot", "difficulty", "music", "boost_item_chance")}
        self._player_start = dict(data["player_start"])
        self._texts = []
        self._message = None
        self._message_time = 0.0

        camera = scene._camera
        focus_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self._focus = create_sprite(self._world, camera.pos + pygame.Vector2(camera.view.size) / 2,
                                    pygame.Vector2(0, 0), focus_surface)
        self._world.add_component(self._focus, CTagWorld())
        self._world.add_component(self._focus, CTagEditor())
        self._camera_target = camera.target
        camera.target = self._focus

        marker_surface = scene._p_ship.sprites[0]
        self._marker = create_sprite(self._world, pygame.Vector2(0, 0), pygame.Vector2(0, 0),
                                     marker_surface)
        self._world.add_component(self._marker, CTagWorld())
        self._world.add_component(self._marker, CTagEditor())
        self._world.add_component(self._marker, CBlink(marker_surface, self._cfg["marker_blink"]))
        self._move_marker()
        self._refresh_texts()

    def _move_marker(self):
        size = pygame.Vector2(self._world.component_for_entity(self._marker, CSurface).area.size)
        self._world.component_for_entity(self._marker, CTransform).pos = \
            pygame.Vector2(self._player_start["x"], self._player_start["y"]) - size / 2

    def _text(self, text: str, info: dict, color: dict) -> int:
        entity = create_text(self._world, text, self._scene._font, self._cfg["size"], color,
                             info["position"], info.get("align", "left"), layer=6)
        self._world.add_component(entity, CTagEditor())
        return entity

    def _refresh_texts(self):
        """Titulo, opciones actuales, ayuda y mensaje"""
        for entity in self._texts:
            self._world.delete_entity(entity)
        cfg = self._cfg
        options = self._options
        music = DEFAULT if options["music"] < 0 else str(options["music"] + 1)
        values = {"special_shot": "ON" if options["special_shot"] else "OFF",
                  "difficulty": options["difficulty"], "music": music,
                  "boost_item_chance": f"{round(options['boost_item_chance'] * 100)}%"}
        self._texts = [self._text(cfg["title"]["text"], cfg["title"], cfg["title"]["color"])]
        for i, (key, label) in enumerate(cfg["options"]):
            pos = {"x": cfg["options_x"], "y": cfg["options_y"] + i * cfg["line_height"]}
            self._texts.append(self._text(label.format(values[key]), {"position": pos},
                                          cfg["option_color"]))
        for i, line in enumerate(cfg["help"]):
            pos = {"x": cfg["help_x"], "y": cfg["help_y"] + i * cfg["line_height"]}
            self._texts.append(self._text(line, {"position": pos}, cfg["help_color"]))
        if self._message:
            msg = cfg["message"]
            self._texts.append(self._text(self._message, msg, msg["color"]))

    def _say(self, message: str):
        self._message = message
        self._message_time = self._cfg["message"]["time"]
        self._refresh_texts()

    def _screen_to_world(self, screen_pos) -> pygame.Vector2:
        camera = self._scene._camera
        size = self._scene._world_size
        rel = pygame.Vector2(screen_pos) - pygame.Vector2(camera.view.topleft)
        return pygame.Vector2((camera.pos.x + rel.x) % size["w"], (camera.pos.y + rel.y) % size["h"])

    def _bases(self) -> list:
        return [entity for entity, c_lo in self._world.get_component(CLevelObject)
                if c_lo.object_type == "enemy_base" and self._world.entity_exists(entity)]

    def _base_at(self, point: pygame.Vector2):
        for entity in self._bases():
            combat = self._world.component_for_entity(entity, CEnemyBaseCombat)
            size = pygame.Vector2(combat.get_size())
            center = self._world.component_for_entity(entity, CTransform).pos + size / 2
            delta = shortest_delta(center, point, self._scene._world_size)
            if abs(delta.x) <= size.x / 2 and abs(delta.y) <= size.y / 2:
                return entity
        return None

    def _base_data(self, entity: int) -> dict:
        combat = self._world.component_for_entity(entity, CEnemyBaseCombat)
        core = combat.get_core_center(self._world.component_for_entity(entity, CTransform).pos)
        size = self._scene._world_size
        return {"position": {"x": round(core.x % size["w"]), "y": round(core.y % size["h"])},
                "orientation": combat.orientation,
                "core_mode": self._world.component_for_entity(entity, CBaseCore).mode}

    def _add_base(self, base: dict):
        entity = create_enemy_base(self._world, dict(self._cfg["base_defaults"], **base))
        self._scene._setup_base(entity)

    def _set_bases(self, bases: list):
        for entity in self._bases():
            self._world.delete_entity(entity)
        for base in bases:
            self._add_base(base)

    def _replace_base(self, entity: int, key: str, values: tuple):
        base = self._base_data(entity)
        base[key] = values[1] if base[key] == values[0] else values[0]
        self._world.delete_entity(entity)
        self._add_base(base)

    def data(self) -> dict:
        """Ronda editada en el formato que se guarda"""
        return dict(self._options, enemy_bases=[self._base_data(e) for e in self._bases()],
                    player_start=dict(self._player_start))

    def _load(self, data: dict):
        self._set_bases(data["enemy_bases"])
        self._player_start = dict(data["player_start"])
        self._options = {key: data[key] for key in self._options}
        self._move_marker()
        self._scene._preview_music(self._options["music"])

    def _cycle_option(self, key: str):
        options = self._options
        if key == "special_shot":
            options[key] = not options[key]
        elif key == "difficulty":
            order = [DEFAULT] + list(self._cfg["difficulties"])
            options[key] = order[(order.index(options[key]) + 1) % len(order)]
        elif key == "music":
            tracks = len(self._scene._music_cfg.get("levels", []))
            options[key] = options[key] + 1 if options[key] + 1 < tracks else -1
            self._scene._preview_music(options[key])
        else:
            values = self._cfg["boost_chances"]
            options[key] = next((v for v in values if v > options[key] + 1e-6), values[0])

    def on_click(self, screen_pos, button: int):
        if not self._scene._camera.view.collidepoint(screen_pos):
            return
        point = self._screen_to_world(screen_pos)
        if button == 1:
            self._add_base({"position": {"x": round(point.x), "y": round(point.y)}})
        elif button == 3:
            entity = self._base_at(point)
            if entity is not None:
                self._world.delete_entity(entity)

    def on_action(self, name: str):
        session = self._scene._session
        level = session.level
        save = ServiceLocator.save_service
        point = self._screen_to_world(pygame.mouse.get_pos())
        if name in ("EDITOR_ROTATE", "EDITOR_CORE"):
            entity = self._base_at(point)
            if entity is not None and name == "EDITOR_ROTATE":
                self._replace_base(entity, "orientation", ("horizontal", "vertical"))
            elif entity is not None:
                self._replace_base(entity, "core_mode", ("open", "cycle"))
        elif name == "EDITOR_START":
            self._player_start = {"x": round(point.x), "y": round(point.y)}
            self._move_marker()
        elif name in self._cfg["option_keys"]:
            self._cycle_option(self._cfg["option_keys"][name])
            self._refresh_texts()
        elif name == "EDITOR_SAVE":
            levels = save.load_levels()
            levels[str(level)] = self.data()
            save.save_levels(levels)
            session.edited_levels[level] = self.data()
            self._say(self._cfg["texts"]["saved"])
        elif name == "EDITOR_LOAD":
            saved = save.load_levels().get(str(level))
            if saved is None:
                self._say(self._cfg["texts"]["nothing_saved"])
            else:
                self._load(saved)
                self._say(self._cfg["texts"]["loaded"])
        elif name == "EDITOR_RESET":
            levels = save.load_levels()
            levels.pop(str(level), None)
            save.save_levels(levels)
            session.edited_levels.pop(level, None)
            self._load(self._original)
            self._say(self._cfg["texts"]["reset"])

    def update(self, delta_time: float, direction: pygame.Vector2):
        """Camara libre con las flechas; el resto del juego sigue congelado"""
        world = self._world
        size = self._scene._world_size
        c_t = world.component_for_entity(self._focus, CTransform)
        c_t.pos += direction * self._cfg["camera_speed"] * delta_time
        c_t.pos.x %= size["w"]
        c_t.pos.y %= size["h"]
        system_blink(world, delta_time)
        system_camera(world)
        system_star_parallax(world, self._scene._camera.delta)
        system_star_wrap(world, self._scene._play_area)
        system_radar(world, self._scene._radar_cfg, size)
        if self._message:
            self._message_time -= delta_time
            if self._message_time <= 0:
                self._message = None
                self._refresh_texts()

    def close(self) -> bool:
        """Guarda lo editado en la sesion; no deja salir sin bases"""
        if not self._bases():
            self._say(self._cfg["texts"]["need_base"])
            return False
        self._scene._session.edited_levels[self._scene._session.level] = self.data()
        return True
