"""Clase base de todas las escenas del juego (patron Escena)."""

from typing import TYPE_CHECKING
import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_rendering import system_rendering

if TYPE_CHECKING:
    from src.engine.game_engine import GameEngine


class Scene:
    def __init__(self, game_engine:"GameEngine") -> None:
        self.ecs_world = esper.World()
        self._game_engine = game_engine
        self.screen_rect = self._game_engine.screen.get_rect()

    def do_process_events(self, event:pygame.event.Event):
        system_input_player(self.ecs_world, event, self.do_action)

    def simulate(self, delta_time:float):
        self.do_update(delta_time)
        self.ecs_world._clear_dead_entities()

    def clean(self):
        self.ecs_world.clear_database()
        self.do_clean()

    def switch_scene(self, new_scene_name:str):
        self._game_engine.switch_scene(new_scene_name)

    # --- Metodos que cada escena concreta sobreescribe ---
    def do_create(self):
        pass

    def do_update(self, delta_time:float):
        pass

    def do_draw(self, screen:pygame.Surface):
        system_rendering(self.ecs_world, screen)

    def do_action(self, action:CInputCommand):
        pass

    def do_clean(self):
        pass