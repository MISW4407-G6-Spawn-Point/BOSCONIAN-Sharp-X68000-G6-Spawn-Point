"""Escena de juego (nivel)."""

import pygame

from src.create.prefab_creator import (create_blast_off, create_camera, create_enemy_spawner,
                                       create_hud, create_input_play, create_level_objects,
                                       create_pause_menu, create_pause_page,
                                       create_player_bullets,
                                       create_player_ship, create_radar_dot,
                                       create_starfield,
                                       create_timed_spawner,
                                       create_special_hud, create_special_shot_message,
                                       create_boost_item_spawner,
                                       player_shot_angles)
from src.ecs.components.c_base_turrets import CBaseTurrets
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_condition_display import CConditionDisplay
from src.ecs.components.c_cutscene import CCutscene
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_player_weapon import CPlayerWeapon
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_pause import CTagPause
from src.ecs.systems.s_base_core import system_base_core
from src.ecs.systems.s_base_turrets import system_base_turrets
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_bullet_screen import system_bullet_screen
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_collision_bullet_level_object import system_collision_bullet_level_object
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_collision_enemy_bounce import system_collision_enemy_bounce
from src.ecs.systems.s_collision_enemy_obstacle import system_collision_enemy_obstacle
from src.ecs.systems.s_collision_indestructible import system_collision_indestructible
from src.ecs.systems.s_mine_explosion import system_mine_explosion
from src.ecs.systems.s_collision_player import system_collision_player
from src.ecs.systems.s_condition import system_condition
from src.ecs.systems.s_cutscene import system_cutscene
from src.ecs.systems.s_enemy_base_eye import system_enemy_base_eye
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_enemy_state import system_enemy_state
from src.ecs.systems.s_explosion import system_explosion
from src.ecs.systems.s_hi_score import system_hi_score
from src.ecs.systems.s_lifetime import system_lifetime
from src.ecs.systems.s_lives_hud import system_lives_hud
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_ship import DIRECTIONS, system_player_ship
from src.ecs.systems.s_player_state import kill_player, respawn_player, system_player_state
from src.ecs.systems.s_radar import system_radar
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_score_display import system_score_display
from src.ecs.systems.s_sprite_animation import system_sprite_animation
from src.ecs.systems.s_star_parallax import system_star_parallax
from src.ecs.systems.s_star_wrap import system_star_wrap
from src.ecs.systems.s_world_wrap import system_world_wrap
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator
from src.ecs.systems.s_alert_overlay import system_alert_overlay
from src.ecs.systems.s_formation import system_formation
from src.ecs.systems.s_score_popup import system_score_popup
from src.ecs.systems.s_spy import system_spy
from src.ecs.systems.s_timed_spawner import system_timed_spawner
from src.ecs.components.c_special_power import CSpecialPower
from src.ecs.systems.s_special_power import activate_boost, system_special_power
from src.ecs.systems.s_boost_item import system_boost_item
from src.ecs.systems.s_special_hud import system_special_hud

_DIRECTION_INPUTS = {
    "PLAYER_LEFT": pygame.Vector2(-1, 0),
    "PLAYER_RIGHT": pygame.Vector2(1, 0),
    "PLAYER_UP": pygame.Vector2(0, -1),
    "PLAYER_DOWN": pygame.Vector2(0, 1),
}


_PAUSE_PAGES = {
    "SHOW_INSTRUCTIONS": "instructions_scene",
    "SHOW_CREDITS": "credits_scene",
}


class PlayScene(Scene):
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self._session = game_engine.session
        self._god_mode = False

    def do_create(self):
        interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        world_cfg = ServiceLocator.configs_service.get("assets/cfg/world.json")
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        levels_cfg = ServiceLocator.configs_service.get("assets/cfg/level.json")
        self._level_cfg = levels_cfg[self._level_name(levels_cfg)]
        self._player_cfg = ServiceLocator.configs_service.get("assets/cfg/player.json")
        self._game_cfg = ServiceLocator.configs_service.get("assets/cfg/game.json")
        self._enemies_cfg = ServiceLocator.configs_service.get("assets/cfg/enemies.json")
        self._bullet_cfg = ServiceLocator.configs_service.get("assets/cfg/bullet.json")
        self._enemy_bullet_cfg = self._bullet_cfg["enemy"]
        self._explosion_cfg = ServiceLocator.configs_service.get(
            "assets/cfg/explosion.json"
        )
        self._special_cfg = ServiceLocator.configs_service.get("assets/cfg/special.json")
        self._scenes_cfg = scenes_cfg["PLAY_SCENE"]
        self._levels_cfg = levels_cfg
        self._play_area = interface_cfg["play_area"]
        self._world_size = world_cfg["world_size"]
        self._player_start = world_cfg["player_start"]
        self._radar_cfg = interface_cfg["hud"]["radar"]
        self._pause_cfg = interface_cfg["pause"]
        self._font = interface_cfg["font"]
        self._alerts_cfg = interface_cfg["alerts"]
        self._formations_cfg = ServiceLocator.configs_service.get("assets/cfg/formations.json")
        self._spy_cfg = ServiceLocator.configs_service.get("assets/cfg/spy.json")
        self._interface_cfg = interface_cfg
        self._paused = False
        self._pause_view = None
        self._held_directions = set()

        create_starfield(self.ecs_world, world_cfg, self._play_area, in_menu=False)
        self._player_entity = create_player_ship(self.ecs_world, self._player_cfg,
                                                self._player_start)
        self.ecs_world.add_component(self._player_entity,
                                    CSpecialPower(self._special_cfg["start_charges"],
                                                  self._special_cfg["max_charges"],
                                                  self._player_cfg["max_speed"]))
        special_shot = self._level_cfg.get("special_shot", False)
        self.ecs_world.add_component(self._player_entity, CPlayerWeapon(special_shot))
        obstacles_cfg = ServiceLocator.configs_service.get("assets/cfg/obstacles.json")
        self._difficulty_cfg = ServiceLocator.configs_service.get("assets/cfg/difficulty.json")
        level_with_obstacles = dict(self._level_cfg)
        level_with_obstacles.setdefault("obstacles", self._scaled_obstacles(obstacles_cfg))
        level_entities = create_level_objects(self.ecs_world, level_with_obstacles, obstacles_cfg,self._world_size, self._player_start)
        self._p_ship = self.ecs_world.component_for_entity(self._player_entity, CPlayerShip)
        self._p_state = self.ecs_world.component_for_entity(self._player_entity, CPlayerState)
        camera_entity = create_camera(self.ecs_world, self._player_entity,
                                      self._play_area, self._world_size)
        self._camera = self.ecs_world.component_for_entity(camera_entity, CCamera)
        create_hud(
            self.ecs_world,
            interface_cfg["hud"],
            interface_cfg["font"],
            self._level_cfg["condition"],
            self._session.score,
            self._session.level,
            self._session.hi_score,
            self._session.lives,
        )
        create_special_hud(self.ecs_world, interface_cfg["hud"]["special"], interface_cfg["font"],
                           self._special_cfg["start_charges"], self._special_cfg["name"])
        item_cfg = self._special_cfg["item"]
        create_boost_item_spawner(self.ecs_world, item_cfg["interval"],
                                  self._level_cfg.get("boost_item_chance", item_cfg["chance"]))
        create_radar_dot(self.ecs_world, self._player_entity,
                        self._radar_cfg["dot_size"], self._radar_cfg["player_color"])
        for entity in level_entities:
            level_object = self.ecs_world.try_component(entity, CLevelObject)
            if level_object is not None and level_object.object_type == "enemy_base":
                combat = self.ecs_world.component_for_entity(entity, CEnemyBaseCombat)
                self.ecs_world.add_component(entity, CBaseTurrets(
                    len(combat.node_centers), self._enemy_bullet_cfg["interval_min"],
                    self._enemy_bullet_cfg["interval_max"]))
                create_radar_dot(
                    self.ecs_world,
                    entity,
                    self._radar_cfg["dot_size"],
                    self._radar_cfg["base_color"],
                )
        create_enemy_spawner(self.ecs_world, self._level_cfg.get(
            "enemy_spawn", self._scaled_enemy_spawn()))
        create_timed_spawner(self.ecs_world, "formation",
                             self._scaled(self._difficulty_cfg["formation_interval"]))
        create_timed_spawner(self.ecs_world, "spy", self._spy_cfg["interval"],
                             self._scaled(self._difficulty_cfg["spy_chance"]))
        self._special_shot = special_shot
        create_blast_off(self.ecs_world, interface_cfg["blast_off"], self._font,
                         DIRECTIONS[self._p_ship.dir_index])
        create_input_play(self.ecs_world)
        self._music_cfg = ServiceLocator.configs_service.get("assets/cfg/music.json")
        self._play_level_music()
        ServiceLocator.sounds_service.play_cfg(self._game_cfg.get("sound_level_start"))
        system_camera(self.ecs_world)
        system_radar(self.ecs_world, self._radar_cfg, self._world_size)

    def _play_level_music(self):
        """Pista de la ronda actual (ciclo de music.json "levels")"""
        tracks = self._music_cfg.get("levels")
        if tracks:
            music = tracks[(self._session.level - 1) % len(tracks)]
            ServiceLocator.sounds_service.play_music(music["track"], music["volume"])

    def _on_condition_change(self, phase:str):
        """Suena una vez por cambio; en ROJA cambia la musica"""
        ServiceLocator.sounds_service.play_cfg(self._alerts_cfg.get("sounds", {}).get(phase))
        red_music = self._music_cfg.get("red_alert")
        if phase == "RED" and red_music:
            ServiceLocator.sounds_service.play_music(red_music["track"], red_music["volume"])

    def _scaled(self, rule:dict) -> float:
        """start + per_round * (ronda - 1), sin pasar de limit (hacia arriba o hacia abajo)."""
        value = rule["start"] + rule["per_round"] * (self._session.level - 1)
        return max(value, rule["limit"]) if rule["per_round"] < 0 else min(value, rule["limit"])

    def _scaled_enemy_spawn(self) -> dict:
        """Cada ronda salen enemigos mas seguido, mas a la vez y apuntan mejor."""
        spawn_cfg = dict(self._enemies_cfg["default_spawn"])
        rules = self._difficulty_cfg["enemy_spawn"]
        spawn_cfg["interval"] = self._scaled(rules["interval"])
        spawn_cfg["max_enemies"] = round(self._scaled(rules["max_enemies"]))
        spawn_cfg["accuracy"] = self._scaled(rules["accuracy"])
        return spawn_cfg

    def _scaled_obstacles(self, obstacles_cfg:dict) -> dict:
        """Cada ronda hay mas rocas y minas (default_counts * multiplicador)."""
        mult = self._scaled(self._difficulty_cfg["obstacles_multiplier"])
        return {obstacle_type: round(count * mult)
                for obstacle_type, count in obstacles_cfg["default_counts"].items()}

    def _level_name(self, levels_cfg:dict) -> str:
        for name in (f"round{self._session.level}", f"level{self._session.level}"):
            if name in levels_cfg:
                return name
        self._session.level = 1
        return "round1" if "round1" in levels_cfg else "level1"

    def _has_next_level(self) -> bool:
        next_level = self._session.level + 1
        return f"round{next_level}" in self._levels_cfg or f"level{next_level}" in self._levels_cfg

    def do_update(self, delta_time:float):
        system_blink(self.ecs_world, delta_time)
        if self._paused:
            self._update_pause_page(delta_time)
            return
        star_offset = system_cutscene(self.ecs_world, delta_time, self._on_cutscene_end)
        if star_offset is not None:
            system_star_parallax(self.ecs_world, star_offset)
            system_star_wrap(self.ecs_world, self._play_area)
            system_score_display(self.ecs_world)
            return
        system_condition(self.ecs_world, delta_time, self._on_condition_change)
        system_enemy_base_eye(self.ecs_world, delta_time)
        system_base_core(self.ecs_world, self._player_entity, self._world_size,
                         self._enemies_cfg, self._player_cfg["max_speed"])
        system_sprite_animation(self.ecs_world, delta_time)
        system_special_power(self.ecs_world, self._player_entity, self._special_cfg, delta_time)
        system_player_ship(self.ecs_world, delta_time)
        system_enemy_spawner(self.ecs_world, self._player_entity, self._enemies_cfg,
                             self._world_size, self._player_cfg["max_speed"], delta_time)
        system_enemy_state(self.ecs_world, self._player_entity, self._world_size,
                           self._enemies_cfg["despawn_distance"], delta_time)
        system_timed_spawner(self.ecs_world, self._player_entity, self._camera,
                             self._formations_cfg, self._spy_cfg, self._enemies_cfg,
                             self._player_cfg["max_speed"], delta_time)
        system_formation(self.ecs_world, self._player_entity, self._world_size,
                         self._formations_cfg["spacing"],
                         self._enemies_cfg["despawn_distance"], delta_time)
        system_spy(self.ecs_world, self._player_entity, self._camera, self._world_size)
        system_base_turrets(self.ecs_world, self._player_entity, self._world_size,
                            self._enemy_bullet_cfg, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_boost_item(self.ecs_world, self._player_entity, self._special_cfg,
                          self._world_size, self._radar_cfg, delta_time)
        system_collision_indestructible(self.ecs_world, self._player_entity, self._world_size,
                                        self._explosion_cfg, self._god_mode,
                                        self._on_player_hit)
        system_collision_bullet_level_object(
            self.ecs_world,
            self._explosion_cfg,
        )
        if not self._god_mode:
            system_collision_player(self.ecs_world, self._player_entity,
                                    self._explosion_cfg, self._on_player_hit)
        system_collision_enemy_bullet(self.ecs_world, self._player_entity, self._explosion_cfg,
                                      self._god_mode, self._on_player_hit)
        system_collision_enemy_obstacle(self.ecs_world, self._world_size, self._explosion_cfg)
        system_collision_enemy_bounce(self.ecs_world, self._world_size)
        system_mine_explosion(self.ecs_world, self._player_entity, self._world_size,
                              self._explosion_cfg, self._god_mode, self._on_player_hit)
        system_player_state(self.ecs_world, self._player_entity, delta_time,
                            self._on_player_respawn)
        system_explosion(self.ecs_world, delta_time)
        system_score_popup(self.ecs_world, delta_time)
        system_lifetime(self.ecs_world, delta_time)
        system_alert_overlay(self.ecs_world, self._alerts_cfg, self._font)
        self._update_score()
        system_special_hud(self.ecs_world, self._player_entity)
        system_score_display(self.ecs_world)
        system_lives_hud(self.ecs_world, self._session.lives)
        if not self.ecs_world.get_component(CEnemyBaseCombat):
            self._next_level()
        system_world_wrap(self.ecs_world, self._world_size["w"], self._world_size["h"])
        system_camera(self.ecs_world)
        system_star_parallax(self.ecs_world, self._camera.delta)
        system_star_wrap(self.ecs_world, self._play_area)
        system_bullet_screen(self.ecs_world, self._camera)
        system_radar(self.ecs_world, self._radar_cfg, self._world_size)

    def _update_score(self):
        score = system_hi_score(self.ecs_world)
        if self._session.update_score(score):
            ServiceLocator.sounds_service.play_cfg(self._game_cfg["sound_extra_life"])

    def _next_level(self):
        if self._has_next_level():
            self._session.level += 1
            self.switch_scene("PLAY_SCENE")
        else:
            self.switch_scene(self._scenes_cfg["victory_scene"])

    def _on_cutscene_end(self):
        if self._special_shot:
            create_special_shot_message(self.ecs_world, self._interface_cfg["special_shot_message"],
                                        self._font)

    def _can_act(self) -> bool:
        """Dispara/usa especial solo vivo y fuera del BLAST OFF"""
        return self._p_state.state == PlayerState.ALIVE and \
            not self.ecs_world.get_component(CCutscene)

    def _fire(self):
        """Z (o el piloto de la demo): 2 balas, o 4 con el disparo especial del nivel"""
        if not self._can_act():
            return
        num_bullets = len(self.ecs_world.get_component(CTagBullet))
        angles = player_shot_angles(self.ecs_world, self._player_entity, self._bullet_cfg)
        if num_bullets + len(angles) <= self._bullet_cfg["max_bullets"]:
            create_player_bullets(self.ecs_world, self._player_entity, self._bullet_cfg, angles)

    def _on_player_hit(self):
        kill_player(self.ecs_world, self._player_entity,
                    self._player_cfg["death"], self._explosion_cfg)

    def _on_player_respawn(self):
        """Si quedan vidas de reserva, reaparece; si no, GAME OVER."""
        if self._session.lives > 0:
            self._session.lives -= 1
            self._session.lives_lost += 1
            respawn_player(self.ecs_world, self._player_entity, self._player_start)
        else:
            self._session.lives_lost += 1
            self._p_state.timer = float("inf")
            self.switch_scene(self._scenes_cfg["game_over_scene"])

    def do_draw(self, screen:pygame.Surface):
        hide_world = self._paused and self._pause_cfg["hide_world"]
        system_rendering(self.ecs_world, screen, self._camera, hide_world)

    def _clear_pause_texts(self):
        for entity, _ in self.ecs_world.get_component(CTagPause):
            self.ecs_world.delete_entity(entity)

    def _show_pause_view(self, view:str, page_index:int = 0):
        """view: "menu" o el nombre de la config de paginas (instructions_scene, credits_scene)"""
        self._clear_pause_texts()
        self._pause_view = view
        if view == "menu":
            create_pause_menu(self.ecs_world, self._pause_cfg, self._font)
            return
        page_cfg = self._interface_cfg[view]
        self._page_index = page_index
        self._page_time = page_cfg["page_time"]
        create_pause_page(self.ecs_world, page_cfg, self._pause_cfg["page_hint"], self._font,
                          page_index)

    def _update_pause_page(self, delta_time:float):
        """Las paginas con mas de una hoja rotan solas, como en su escena"""
        if self._pause_view in (None, "menu"):
            return
        page_cfg = self._interface_cfg[self._pause_view]
        self._page_time -= delta_time
        if self._page_time <= 0 and len(page_cfg["pages"]) > 1:
            self._show_pause_view(self._pause_view,
                                  (self._page_index + 1) % len(page_cfg["pages"]))

    def _toggle_pause(self):
        if self._paused and self._pause_view != "menu":
            self._show_pause_view("menu")
            return
        self._paused = not self._paused
        if self._paused:
            ServiceLocator.sounds_service.pause_music()
            self._show_pause_view("menu")
        else:
            ServiceLocator.sounds_service.unpause_music()
            self._clear_pause_texts()
            self._pause_view = None

    def _toggle_pause_page(self, view:str):
        """I o C: abre la pagina; la misma tecla vuelve al menu"""
        self._show_pause_view("menu" if self._pause_view == view else view)

    def do_action(self, action:CInputCommand):
        if action.name == "BACK_TO_TITLE" and action.phase == CommandPhase.STARTED:
            self.switch_scene(self._scenes_cfg["back_scene"])
            return

        if action.name == "PAUSE" and action.phase == CommandPhase.STARTED:
            self._toggle_pause()
            return

        if action.name in _PAUSE_PAGES and action.phase == CommandPhase.STARTED:
            if self._paused:
                self._toggle_pause_page(_PAUSE_PAGES[action.name])
            return

        if action.name in _DIRECTION_INPUTS:
            if action.phase == CommandPhase.STARTED:
                self._held_directions.add(action.name)
            elif action.phase == CommandPhase.END:
                self._held_directions.discard(action.name)
            self._p_ship.input = sum((_DIRECTION_INPUTS[name] for name in self._held_directions),
                                     pygame.Vector2(0, 0))
            return

        if self._paused or action.phase != CommandPhase.STARTED:
            return

        if action.name == "PLAYER_FIRE":
            self._fire()

        elif action.name == "PLAYER_SPECIAL" and self._can_act():
            activate_boost(self.ecs_world, self._player_entity, self._special_cfg)
        elif action.name == "CHEAT_NEXT_LEVEL":
            self._next_level()
        elif action.name == "CHEAT_GOD_MODE":
            self._god_mode = not self._god_mode
        elif action.name == "CHEAT_RED_ALERT":
            for _, condition in self.ecs_world.get_component(CConditionDisplay):
                condition.elapsed_time = max(condition.elapsed_time, condition.red_time)