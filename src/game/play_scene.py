"""Escena de juego (nivel)."""

from src.create.prefab_creator import create_hud, create_input_play, create_starfield
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

class PlayScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        self._back_scene = scenes_cfg["PLAY_SCENE"]["back_scene"]

        create_starfield(self.ecs_world, world_cfg, interface_cfg["play_area"])
        create_hud(self.ecs_world, interface_cfg["hud"], interface_cfg["font"])
        create_input_play(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)

    def do_action(self, action:CInputCommand):
        if action.name == "BACK_TO_TITLE" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._back_scene)