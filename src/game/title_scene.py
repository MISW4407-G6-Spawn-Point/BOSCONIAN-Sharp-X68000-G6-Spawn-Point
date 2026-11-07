"""Escena de titulo."""

from src.create.prefab_creator import create_text, create_input_title
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class TitleScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        font = interface_cfg["font"]
        for key in ("title", "press_start"):
            info = interface_cfg["title_scene"][key]
            create_text(self.ecs_world, info["text"], font, info["size"],
                        info["color"], info["position"])
        create_input_title(self.ecs_world)

    def do_action(self, action:CInputCommand):
        if action.name == "START_GAME" and action.phase == CommandPhase.STARTED:
            self.switch_scene("PLAY_SCENE")