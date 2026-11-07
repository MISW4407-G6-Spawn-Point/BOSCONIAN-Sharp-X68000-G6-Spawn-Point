"""Escena de juego (nivel)."""

from src.create.prefab_creator import create_text, create_input_play
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_movement import system_movement
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class PlayScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        font = interface_cfg["font"]
        for key in ("round", "hint"):
            info = interface_cfg["play_scene"][key]
            create_text(self.ecs_world, info["text"], font, info["size"],
                        info["color"], info["position"])
        create_input_play(self.ecs_world)

    def do_update(self, delta_time:float):
        system_movement(self.ecs_world, delta_time)

    def do_action(self, action:CInputCommand):
        if action.name == "BACK_TO_TITLE" and action.phase == CommandPhase.STARTED:
            self.switch_scene("TITLE_SCENE")