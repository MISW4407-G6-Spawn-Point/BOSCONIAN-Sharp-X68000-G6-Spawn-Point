"""Escena de paginas de texto (instrucciones, creditos). Se configura en interface.json."""

from src.create.prefab_creator import (create_hud, create_input_title,
                                       create_scene_timer, create_starfield, create_text,
                                       create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class TextPageScene(Scene):
    def __init__(self, game_engine, scene_name:str, cfg_name:str) -> None:
        super().__init__(game_engine)
        self._scene_name = scene_name
        self._cfg_name = cfg_name

    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        scene_cfg = scenes_cfg[self._scene_name]
        self._font = interface_cfg["font"]
        self._page_cfg = interface_cfg[self._cfg_name]
        self._start_scene = scene_cfg["start_scene"]
        self._back_scene = scene_cfg["back_scene"]
        self._play_area = interface_cfg["play_area"]

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], self._font, None, 0, 1,
                   self._game_engine.session.hi_score)
        create_texts(self.ecs_world, [self._page_cfg["title"]], self._font)
        create_scene_timer(self.ecs_world, scene_cfg)
        create_input_title(self.ecs_world)

        self._page_entities = []
        self._page_index = 0
        self._page_time = self._page_cfg["page_time"]
        self._show_page()

    def _show_page(self):
        """Borra la pagina anterior y crea las lineas de la actual"""
        for entity in self._page_entities:
            self.ecs_world.delete_entity(entity)
        cfg = self._page_cfg
        page = cfg["pages"][self._page_index]
        self._page_entities = []
        for i, line in enumerate(page["lines"]):
            pos = {"x": cfg["line_x"], "y": cfg["line_y"] + i * cfg["line_height"]}
            self._page_entities.append(create_text(
                self.ecs_world, line, self._font, cfg["size"],
                page.get("color", cfg["color"]), pos, align=cfg["align"]))
        if len(cfg["pages"]) > 1:
            marker = cfg["page_marker"]
            text = marker["text"].format(page=self._page_index + 1, total=len(cfg["pages"]))
            self._page_entities.append(create_text(
                self.ecs_world, text, self._font, cfg["size"], marker["color"],
                marker["position"]))

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)
        self._page_time -= delta_time
        if self._page_time <= 0 and len(self._page_cfg["pages"]) > 1:
            self._page_time = self._page_cfg["page_time"]
            self._page_index = (self._page_index + 1) % len(self._page_cfg["pages"])
            self._show_page()

    def do_action(self, action:CInputCommand):
        if action.phase != CommandPhase.STARTED:
            return
        if action.name == "START_GAME":
            self.switch_scene(self._start_scene)
        elif action.name == "BACK_TO_TITLE":
            self.switch_scene(self._back_scene)
