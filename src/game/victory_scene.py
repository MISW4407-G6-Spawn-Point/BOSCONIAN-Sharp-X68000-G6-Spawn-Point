"""Escena de victoria: al terminar todos los niveles."""

from src.create.prefab_creator import (create_hud, create_input_continue, create_scene_timer,
                                       create_starfield, create_text, create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class VictoryScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        session = self._game_engine.session
        victory_cfg = interface_cfg["victory_scene"]
        scene_cfg = scenes_cfg["VICTORY_SCENE"]
        self._next_scene = scene_cfg["record_scene"] if session.is_new_record() \
            else scene_cfg["next_scene"]
        session.save_record()
        self._play_area = interface_cfg["play_area"]

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None,
                   session.score, session.level, session.hi_score, session.lives)
        create_texts(self.ecs_world, victory_cfg["texts"], font)

        stats = victory_cfg["stats"]
        values = {"score": session.score, "lives_lost": session.lives_lost,
                  "continues": session.continues}
        for i, line in enumerate(stats["lines"]):
            create_text(self.ecs_world, line.format(**values), font, stats["size"],
                        stats["color"], {"x": stats["x"], "y": stats["y"] + i * stats["line_height"]})
        create_scene_timer(self.ecs_world, dict(scene_cfg, next_scene=self._next_scene))
        create_input_continue(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def do_action(self, action:CInputCommand):
        if action.name == "CONTINUE" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._next_scene)