"""Escena de derrota: CONTINUE con cuenta regresiva."""

import math

import pygame

from src.create.prefab_creator import (create_hud, create_input_continue, create_starfield,
                                       create_text, create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class GameOverScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        game_cfg = ServiceLocator.configs_service.get("assets/cfg/game.json")
        font = interface_cfg["font"]
        session = self._game_engine.session
        self._scene_cfg = scenes_cfg["GAME_OVER_SCENE"]
        self._play_area = interface_cfg["play_area"]
        self._time = game_cfg["continue_time"]

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None,
                   session.score, session.level, session.hi_score, 0)
        create_texts(self.ecs_world, interface_cfg["game_over_scene"]["texts"], font)

        cd = interface_cfg["game_over_scene"]["countdown"]
        countdown_entity = create_text(self.ecs_world, str(self._time), font, cd["size"],
                                       cd["color"], cd["position"])
        color = pygame.Color(cd["color"]["r"], cd["color"]["g"], cd["color"]["b"])
        self._countdown = CScoreDisplay(cd["position"]["x"], cd["position"]["y"] + cd["size"] / 2,
                                        font, cd["size"], color, self._time, tracks_score=False)
        self.ecs_world.add_component(countdown_entity, self._countdown)
        create_input_continue(self.ecs_world)
        ServiceLocator.sounds_service.play_cfg(interface_cfg["game_over_scene"].get("sound"))

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        if self._time <= 0:
            return
        self._time -= delta_time
        self._countdown.value = max(0, math.ceil(self._time))
        system_score_display(self.ecs_world)
        if self._time <= 0:
            session = self._game_engine.session
            session.save_record()
            self.switch_scene(self._scene_cfg["record_scene"] if session.is_new_record()
                              else self._scene_cfg["next_scene"])

    def do_action(self, action:CInputCommand):
        if action.name == "CONTINUE" and action.phase == CommandPhase.STARTED:
            self._game_engine.session.continue_game()
            self.switch_scene(self._scene_cfg["continue_scene"])