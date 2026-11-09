"""Escena de arranque"""
from src.create.prefab_creator import (create_boot_cursor, create_function_keys,create_scene_timer)
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

class BootScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        boot_cfg = interface_cfg["boot_scene"]
        create_boot_cursor(self.ecs_world, boot_cfg["cursor"])
        create_function_keys(self.ecs_world, boot_cfg["function_keys"], interface_cfg["font"])
        create_scene_timer(self.ecs_world, scenes_cfg["BOOT_SCENE"])

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)