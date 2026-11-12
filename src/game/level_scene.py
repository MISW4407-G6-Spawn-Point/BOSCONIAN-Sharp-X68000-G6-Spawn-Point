"""Escena de presentacion del nivel """
from src.create.prefab_creator import (create_hud, create_scene_timer, create_starfield, create_texts)
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_star_wrap import system_star_wrap

class LevelScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        self._play_area = interface_cfg["play_area"]

        create_starfield(self.ecs_world, world_cfg, interface_cfg["play_area"], in_menu=True)
        create_texts(self.ecs_world, interface_cfg["level_scene"]["texts"], font)
        create_hud(self.ecs_world, interface_cfg["hud"], font)
        create_scene_timer(self.ecs_world, scenes_cfg["LEVEL_SCENE"])

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)