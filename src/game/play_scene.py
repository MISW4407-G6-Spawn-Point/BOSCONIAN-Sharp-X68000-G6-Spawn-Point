"""Escena de juego (nivel)."""

import pygame

from src.create.prefab_creator import (create_camera, create_hud, create_input_play,
                                       create_pause_text, create_player_bullets,
                                       create_player_ship, create_radar_dot,
                                       create_starfield)
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_pause import CTagPause
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_bullet_screen import system_bullet_screen
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_ship import system_player_ship
from src.ecs.systems.s_radar import system_radar
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_star_parallax import system_star_parallax
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.ecs.systems.s_world_wrap import system_world_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

# Comando -> eje que suma a la entrada de la nave
_DIRECTION_INPUTS = {
    "PLAYER_LEFT": pygame.Vector2(-1, 0),
    "PLAYER_RIGHT": pygame.Vector2(1, 0),
    "PLAYER_UP": pygame.Vector2(0, -1),
    "PLAYER_DOWN": pygame.Vector2(0, 1),
}


class PlayScene(Scene):
    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        player_cfg = ServiceLocator.configs_service.get("assets/cfg/player.json")
        self._bullet_cfg = ServiceLocator.configs_service.get("assets/cfg/bullet.json")
        self._back_scene = scenes_cfg["PLAY_SCENE"]["back_scene"]
        self._play_area = interface_cfg["play_area"]
        self._world_size = world_cfg["world_size"]
        self._radar_cfg = interface_cfg["hud"]["radar"]
        self._pause_cfg = interface_cfg["pause"]
        self._font = interface_cfg["font"]
        self._paused = False

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=False)
        self._player_entity = create_player_ship(self.ecs_world, player_cfg,
                                                 world_cfg["player_start"])
        self._p_ship = self.ecs_world.component_for_entity(self._player_entity, CPlayerShip)
        camera_entity = create_camera(self.ecs_world, self._player_entity,
                                      self._play_area, self._world_size)
        self._camera = self.ecs_world.component_for_entity(camera_entity, CCamera)
        create_hud(self.ecs_world, interface_cfg["hud"], interface_cfg["font"])
        create_radar_dot(self.ecs_world, self._player_entity,
                         self._radar_cfg["dot_size"], self._radar_cfg["player_color"])
        create_input_play(self.ecs_world)
        system_camera(self.ecs_world)
        system_radar(self.ecs_world, self._radar_cfg, self._world_size)

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        if self._paused:
            return  # en pausa solo titilan las estrellas
        system_player_ship(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_world_wrap(self.ecs_world, self._world_size["w"], self._world_size["h"])
        system_camera(self.ecs_world)
        system_star_parallax(self.ecs_world, self._camera.delta)
        system_star_wrap(self.ecs_world, self._play_area)
        system_bullet_screen(self.ecs_world, self._camera)
        system_radar(self.ecs_world, self._radar_cfg, self._world_size)

    def do_draw(self, screen:pygame.Surface):
        hide_world = self._paused and self._pause_cfg["hide_world"]
        system_rendering(self.ecs_world, screen, self._camera, hide_world)

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            create_pause_text(self.ecs_world, self._pause_cfg, self._font)
        else:
            for entity, _ in self.ecs_world.get_component(CTagPause):
                self.ecs_world.delete_entity(entity)

    def do_action(self, action:CInputCommand):
        if action.name == "BACK_TO_TITLE" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._back_scene)
            return

        if action.name == "PAUSE" and action.phase == CommandPhase.STARTED:
            self._toggle_pause()
            return


        if action.name in _DIRECTION_INPUTS:
            axis = _DIRECTION_INPUTS[action.name]
            if action.phase == CommandPhase.STARTED:
                self._p_ship.input += axis
            elif action.phase == CommandPhase.END:
                self._p_ship.input -= axis
            return

        if self._paused:
            return

        if action.name == "PLAYER_FIRE" and action.phase == CommandPhase.STARTED:
            num_bullets = len(self.ecs_world.get_component(CTagBullet))
            if num_bullets + 2 <= self._bullet_cfg["max_bullets"]:
                create_player_bullets(self.ecs_world, self._player_entity, self._bullet_cfg)