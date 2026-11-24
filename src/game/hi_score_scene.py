"""Escena de nuevo record: felicita al jugador al superar el puntaje maximo."""

from src.create.prefab_creator import (create_hud, create_input_continue, create_scene_timer,
                                       create_starfield, create_text)
from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class HiScoreScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        session = self._game_engine.session
        record_cfg = interface_cfg["hi_score_scene"]
        self._next_scene = scenes_cfg["HI_SCORE_SCENE"]["next_scene"]
        self._play_area = interface_cfg["play_area"]

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None,
                   session.score, session.level, session.hi_score, session.lives)
        for info in record_cfg["texts"]:
            text = info["text"].format(hi_score=session.hi_score)
            text_entity = create_text(self.ecs_world, text, font, info["size"],
                                      info["color"], info["position"])
            if info.get("blink_time", 0) > 0:
                c_s = self.ecs_world.component_for_entity(text_entity, CSurface)
                self.ecs_world.add_component(text_entity, CBlink(c_s.surf, info["blink_time"]))
        create_scene_timer(self.ecs_world, scenes_cfg["HI_SCORE_SCENE"])
        create_input_continue(self.ecs_world)
        if record_cfg.get("sound"):
            ServiceLocator.sounds_service.play(record_cfg["sound"])

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def do_action(self, action:CInputCommand):
        if action.name == "CONTINUE" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._next_scene)
