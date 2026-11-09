"""Escena de titulo"""

from src.create.prefab_creator import (create_hud, create_input_title, create_logo, 
                                    create_scene_timer, create_starfield, create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class TitleScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        self._next_scene = scenes_cfg["TITLE_SCENE"]["next_scene"]

        create_starfield(self.ecs_world, world_cfg, interface_cfg["play_area"])
        create_logo(self.ecs_world, interface_cfg["title_scene"]["logo"])
        create_texts(self.ecs_world, interface_cfg["title_scene"]["texts"], font)
        create_hud(self.ecs_world, interface_cfg["hud"], font)
        create_scene_timer(self.ecs_world, scenes_cfg["TITLE_SCENE"])
        create_input_title(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def do_action(self, action:CInputCommand):
        if action.name == "START_GAME" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._next_scene)