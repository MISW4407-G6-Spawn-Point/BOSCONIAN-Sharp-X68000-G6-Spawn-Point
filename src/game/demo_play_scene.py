"""Modo atractor: el nivel 1 jugado por una IA, invencible y con una sesion temporal"""

import pygame

from src.create.prefab_creator import create_scene_timer, create_text
from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_cutscene import CCutscene
from src.ecs.components.c_demo_pilot import CDemoPilot
from src.ecs.components.c_surface import CSurface
from src.ecs.systems.s_demo_pilot import system_demo_pilot
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.engine.game_session import GameSession
from src.engine.service_locator import ServiceLocator
from src.game.play_scene import PlayScene


class DemoPlayScene(PlayScene):
    def do_create(self):
        configs = ServiceLocator.configs_service
        self._demo_cfg = configs.get("assets/cfg/scenes.json")["ATTRACT_SCENE"]
        interface_cfg = configs.get("assets/cfg/interface.json")
        real_session = self._game_engine.session
        self._session = GameSession(configs.get("assets/cfg/game.json"))
        self._session.hi_score = real_session.hi_score
        self._session.save_record = lambda: None

        super().do_create()
        self._god_mode = True
        for entity, _ in list(self.ecs_world.get_component(CCutscene)):
            self.ecs_world.remove_component(entity, CCutscene)
            self.ecs_world.delete_entity(entity)
        self._on_cutscene_end()

        self.ecs_world.add_component(self._player_entity, CDemoPilot(
            self._demo_cfg["turn_interval"], self._demo_cfg["fire_interval"],
            self._demo_cfg["avoid_distance"]))
        for info in interface_cfg["attract_scene"]["texts"]:
            entity = create_text(self.ecs_world, info["text"], self._font, info["size"],
                                 info["color"], info["position"], layer=3)
            if info.get("blink_time", 0) > 0:
                c_s = self.ecs_world.component_for_entity(entity, CSurface)
                self.ecs_world.add_component(entity, CBlink(c_s.surf, info["blink_time"]))
        create_scene_timer(self.ecs_world, self._demo_cfg)

    def do_process_events(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.switch_scene(self._demo_cfg["back_scene"])

    def do_update(self, delta_time: float):
        system_demo_pilot(self.ecs_world, self._player_entity, self._world_size, delta_time,
                          self._fire)
        super().do_update(delta_time)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def _next_level(self):
        self.switch_scene(self._demo_cfg["next_scene"])
