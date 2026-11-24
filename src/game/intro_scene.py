"""Intro animado antes del titulo; cualquier tecla lo salta. Pasos en interface.json"""

import pygame

from src.create.prefab_creator import create_hud, create_intro_timeline, create_scene_timer
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_explosion import system_explosion
from src.ecs.systems.s_intro import system_intro
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.ecs.systems.s_stop_at import system_stop_at
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class IntroScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        session = self._game_engine.session
        self._next_scene = scenes_cfg["INTRO_SCENE"]["next_scene"]
        self._play_area = interface_cfg["play_area"]

        create_hud(self.ecs_world, interface_cfg["hud"], interface_cfg["font"], None, 0,
                   session.level, session.hi_score)
        create_intro_timeline(self.ecs_world, interface_cfg["intro_scene"]["steps"])
        create_scene_timer(self.ecs_world, scenes_cfg["INTRO_SCENE"])

    def do_process_events(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.switch_scene(self._next_scene)

    def do_update(self, delta_time: float):
        system_intro(self.ecs_world, delta_time)
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_stop_at(self.ecs_world)
        system_explosion(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)
