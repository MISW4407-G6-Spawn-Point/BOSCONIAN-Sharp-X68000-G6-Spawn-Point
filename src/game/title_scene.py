"""Escena de titulo"""

from src.create.prefab_creator import (create_hud, create_input_title, create_logo, 
                                    create_scene_timer, create_starfield, create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_score_display import system_score_display
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_star_wrap import system_star_wrap


class TitleScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        self._start_scene = scenes_cfg["TITLE_SCENE"]["start_scene"]
        self._instructions_scene = scenes_cfg["TITLE_SCENE"]["instructions_scene"]
        self._credits_scene = scenes_cfg["TITLE_SCENE"]["credits_scene"]
        self._play_area = interface_cfg["play_area"]
        session = self._game_engine.session
        session.new_game()

        create_starfield(self.ecs_world, world_cfg, interface_cfg["play_area"], in_menu=True)
        create_logo(self.ecs_world, interface_cfg["title_scene"]["logo"])
        create_texts(self.ecs_world, interface_cfg["title_scene"]["texts"], font)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None, 0, session.level,
                   session.hi_score)
        create_scene_timer(self.ecs_world, scenes_cfg["TITLE_SCENE"])
        create_input_title(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def do_action(self, action:CInputCommand):
        if action.phase != CommandPhase.STARTED:
            return
        if action.name == "START_GAME":
            self.switch_scene(self._start_scene)
        elif action.name == "SHOW_INSTRUCTIONS":
            self.switch_scene(self._instructions_scene)
        elif action.name == "SHOW_CREDITS":
            self.switch_scene(self._credits_scene)