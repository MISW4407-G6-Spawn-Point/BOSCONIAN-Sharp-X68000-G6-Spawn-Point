"""Escena de texto con scroll (instrucciones, creditos). Se configura en interface.json."""

from src.create.prefab_creator import (create_hud, create_input_title, create_scroll_frame,
                                       create_scroll_text, create_starfield)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_scroll import system_scroll
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
        font = interface_cfg["font"]
        self._scroll_cfg = interface_cfg[self._cfg_name]
        self._next_scene = scene_cfg["next_scene"]
        self._start_scene = scene_cfg["start_scene"]
        self._back_scene = scene_cfg["back_scene"]
        self._play_area = interface_cfg["play_area"]
        self._finished = False

        session = self._game_engine.session
        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None, 0, session.level,
                   session.hi_score)
        create_scroll_text(self.ecs_world, self._scroll_cfg, font, layer=1)
        create_scroll_frame(self.ecs_world, self._scroll_cfg, font, layer=2)
        create_input_title(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        if system_scroll(self.ecs_world, delta_time, self._scroll_cfg["clip_top"]) \
                and not self._finished:
            self._finished = True
            self.switch_scene(self._next_scene)

    def do_action(self, action:CInputCommand):
        if action.phase != CommandPhase.STARTED:
            return
        if action.name == "START_GAME":
            self.switch_scene(self._start_scene)
        elif action.name == "BACK_TO_TITLE":
            self.switch_scene(self._back_scene)
