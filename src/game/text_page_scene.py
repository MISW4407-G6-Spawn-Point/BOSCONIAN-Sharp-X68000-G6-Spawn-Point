"""Instrucciones (paginas que se pasan con las flechas) y creditos (scroll). Config en interface.json"""

from src.create.prefab_creator import (create_hud, create_input_title, create_scroll_frame,
                                       create_scroll_text, create_starfield, create_text_page)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_scroll import system_scroll
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

_PAGE_STEPS = {"PAGE_PREV": -1, "PAGE_NEXT": 1}


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
        self._text_cfg = interface_cfg[self._cfg_name]
        self._next_scene = scene_cfg["next_scene"]
        self._start_scene = scene_cfg["start_scene"]
        self._back_scene = scene_cfg["back_scene"]
        self._idle_time = scene_cfg.get("duration", 0)
        self._time_left = self._idle_time
        self._play_area = interface_cfg["play_area"]
        self._finished = False
        self._paged = "pages" in self._text_cfg

        session = self._game_engine.session
        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], self._font, None, 0, session.level,
                   session.hi_score)
        create_input_title(self.ecs_world)
        if self._paged:
            self._page_entities = []
            self._show_page(0)
        else:
            create_scroll_text(self.ecs_world, self._text_cfg, self._font, layer=1)
            create_scroll_frame(self.ecs_world, self._text_cfg, self._font, layer=2)

    def _show_page(self, page_index:int):
        for entity in self._page_entities:
            self.ecs_world.delete_entity(entity)
        self._page_index = page_index
        self._page_entities = create_text_page(self.ecs_world, self._text_cfg, self._font,
                                               page_index)

    def _go_next(self):
        if not self._finished:
            self._finished = True
            self.switch_scene(self._next_scene)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        if not self._paged:
            if system_scroll(self.ecs_world, delta_time, self._text_cfg["clip_top"]):
                self._go_next()
            return
        self._time_left -= delta_time
        if self._idle_time > 0 and self._time_left <= 0:
            self._go_next()

    def do_action(self, action:CInputCommand):
        if action.phase != CommandPhase.STARTED:
            return
        if action.name == "START_GAME":
            self.switch_scene(self._start_scene)
        elif action.name == "BACK_TO_TITLE":
            self.switch_scene(self._back_scene)
        elif self._paged and action.name in _PAGE_STEPS:
            new_index = self._page_index + _PAGE_STEPS[action.name]
            if 0 <= new_index < len(self._text_cfg["pages"]):
                self._show_page(new_index)
            self._time_left = self._idle_time
