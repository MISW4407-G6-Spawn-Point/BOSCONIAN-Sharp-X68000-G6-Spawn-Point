"""Escena de tabla de puntajes"""

from src.create.prefab_creator import (create_hud, create_icon, create_input_title,
                                       create_scene_timer, create_starfield, create_text,
                                       create_texts)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_scene_timer import system_scene_timer
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class ScoreTableScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        font = interface_cfg["font"]
        table = interface_cfg["score_table_scene"]
        self._start_scene = scenes_cfg["SCORE_TABLE_SCENE"]["start_scene"]
        self._play_area = interface_cfg["play_area"]

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=True)
        create_hud(self.ecs_world, interface_cfg["hud"], font, None, 0, 1,
                   self._game_engine.session.hi_score)
        create_texts(self.ecs_world, [table["title"]], font)
        for i, row in enumerate(table["rows"]):
            y = table["row_y"] + i * table["row_step"]
            create_icon(self.ecs_world, table["image"], row["area"], {"x": table["icon_x"], "y": y})
            create_text(self.ecs_world, row["text"], font, table["size"], table["color"],
                        {"x": table["text_x"], "y": y - table["size"] / 2}, align="left")
        create_texts(self.ecs_world, table["footer"], font)
        create_scene_timer(self.ecs_world, scenes_cfg["SCORE_TABLE_SCENE"])
        create_input_title(self.ecs_world)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_star_wrap(self.ecs_world, self._play_area)
        system_score_display(self.ecs_world)
        system_scene_timer(self.ecs_world, delta_time, self.switch_scene)

    def do_action(self, action:CInputCommand):
        if action.name == "START_GAME" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._start_scene)