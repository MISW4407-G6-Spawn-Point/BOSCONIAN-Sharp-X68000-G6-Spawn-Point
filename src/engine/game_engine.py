"""Modulo del motor del juego."""

import asyncio
import sys
import pygame

from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator
from src.game.title_scene import TitleScene
from src.game.play_scene import PlayScene


class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]),
            0 if sys.platform == "emscripten" else pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])

        # Patron Escena: todas las escenas registradas por nombre
        self._scenes:dict[str, Scene] = {}
        self._scenes["TITLE_SCENE"] = TitleScene(self)
        self._scenes["PLAY_SCENE"] = PlayScene(self)
        self._current_scene:Scene = None
        self._scene_name_to_switch:str = None

    def _load_config_files(self):
        configs = ServiceLocator.configs_service
        self.window_cfg = configs.get("assets/cfg/window.json")

    async def run(self, start_scene_name:str) -> None:
        self.is_running = True
        self._current_scene = self._scenes[start_scene_name]
        self._create()
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            self._handle_switch_scene()
            await asyncio.sleep(0)
        self._do_clean()

    def switch_scene(self, new_scene_name:str):
        """Pide un cambio de escena; se aplica al final del frame actual."""
        self._scene_name_to_switch = new_scene_name

    def _create(self):
        self._current_scene.do_create()

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            self._current_scene.do_process_events(event)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        self._current_scene.simulate(self.delta_time)

    def _draw(self):
        self.screen.fill(self.bg_color)
        self._current_scene.do_draw(self.screen)
        pygame.display.flip()

    def _handle_switch_scene(self):
        if self._scene_name_to_switch is not None:
            self._current_scene.clean()
            self._current_scene = self._scenes[self._scene_name_to_switch]
            self._current_scene.do_create()
            self._scene_name_to_switch = None

    def _do_clean(self):
        if self._current_scene is not None:
            self._current_scene.clean()
        pygame.quit()