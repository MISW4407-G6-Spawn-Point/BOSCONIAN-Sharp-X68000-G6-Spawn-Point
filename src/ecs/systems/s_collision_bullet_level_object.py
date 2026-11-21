import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_level_object import CLevelObject
from src.ecs.components.c_score_display import CScoreDisplay
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.systems.s_condition import reset_condition
from src.create.prefab_creator import create_score_popup


_DESTRUCTIBLE_TYPES = {
    "1-a",
    "1-b",
    "1-c",
    "2-a",
    "2-b",
    "2-c",
    "i",
    "p",
    "e",
    "mine",
    "spy",
}


def _entity_rect(transform: CTransform, surface: CSurface) -> pygame.Rect:
    return pygame.Rect(
        round(transform.pos.x),
        round(transform.pos.y),
        surface.area.width,
        surface.area.height,
    )


def _add_score(world: esper.World, points: int) -> None:
    for _, score_display in world.get_component(CScoreDisplay):
        if score_display.tracks_score:
            score_display.value += points


def _explode_base(
    world: esper.World,
    base_origin: pygame.Vector2,
    base_combat: CEnemyBaseCombat,
    explosion_cfg: dict,
) -> None:
    for node_center in base_combat.node_centers:
        create_explosion(
            world,
            base_origin + node_center,
            explosion_cfg,
        )
    create_explosion(
        world,
        base_origin + pygame.Vector2(49, 40),
        explosion_cfg,
    )


def system_collision_bullet_level_object(
    world: esper.World,
    explosion_cfg: dict,
) -> None:
    impacted_objects = set()
    impacted_bullets = set()
    object_components = list(world.get_components(
        CLevelObject,
        CTransform,
        CSurface,
    ))
    base_components = list(world.get_components(
        CLevelObject,
        CEnemyBaseCombat,
        CTransform,
    ))
    bullet_components = list(world.get_components(
        CTagBullet,
        CTransform,
        CSurface,
    ))

    for bullet_entity, (_, bullet_transform, bullet_surface) in bullet_components:
        if bullet_entity in impacted_bullets:
            continue
        bullet_rect = _entity_rect(bullet_transform, bullet_surface)
        base_hit = False
        for base_entity, (base_object, base_combat, base_transform) in base_components:
            if base_entity in impacted_objects:
                continue
            if base_object.object_type != "enemy_base":
                continue
            base_origin = base_transform.pos
            eye_rect = pygame.Rect(
                round(base_origin.x + 39),
                round(base_origin.y + 30),
                20,
                20,
            )
            hit_index = None
            if base_combat.eye_frame_index == 0 and bullet_rect.colliderect(eye_rect):
                hit_index = -1
            else:
                for index, center in enumerate(base_combat.node_centers):
                    if base_combat.node_destroyed[index]:
                        continue
                    node_rect = pygame.Rect(
                        round(base_origin.x + center.x - 8),
                        round(base_origin.y + center.y - 8),
                        16,
                        16,
                    )
                    if bullet_rect.colliderect(node_rect):
                        hit_index = index
                        break
            if hit_index is None:
                continue

            if hit_index == -1:
                _explode_base(world, base_origin, base_combat, explosion_cfg)
                _add_score(world, base_object.score)
                create_score_popup(world, base_origin + pygame.Vector2(49, 40), base_object.score)
                world.delete_entity(bullet_entity)
                world.delete_entity(base_entity)
                reset_condition(world)
            else:
                new_damage = base_combat.node_damage[hit_index] + 1
                base_combat.node_damage[hit_index] = new_damage
                base_surface = world.component_for_entity(base_entity, CSurface)
                base_surface.surf = base_combat.compose()
                base_surface.area = base_surface.surf.get_rect()
                if new_damage >= 3:
                    base_combat.node_destroyed[hit_index] = True
                    _add_score(world, base_object.node_score)
                world.delete_entity(bullet_entity)
                if base_combat.has_been_destroyed():
                    _explode_base(world, base_origin, base_combat, explosion_cfg)
                    _add_score(world, base_object.score)
                    create_score_popup(world, base_origin + pygame.Vector2(49, 40), base_object.score)
                    world.delete_entity(base_entity)
                    reset_condition(world)
                elif new_damage >= 3:
                    create_explosion(
                        world,
                        base_origin + base_combat.node_centers[hit_index],
                        explosion_cfg,
                    )
            impacted_bullets.add(bullet_entity)
            if not world.entity_exists(base_entity):
                impacted_objects.add(base_entity)
            base_hit = True
            break
        if base_hit:
            continue
        for object_entity, (level_object, object_transform, object_surface) in object_components:
            if object_entity in impacted_objects:
                continue
            if level_object.object_type not in _DESTRUCTIBLE_TYPES:
                continue
            if not bullet_rect.colliderect(_entity_rect(object_transform, object_surface)):
                continue

            object_rect = _entity_rect(object_transform, object_surface)
            create_explosion(
                world,
                pygame.Vector2(object_rect.center),
                explosion_cfg,
            )
            _add_score(world, level_object.score)
            if level_object.object_type == "spy":
                create_score_popup(world, pygame.Vector2(object_rect.center), level_object.score)
            impacted_objects.add(object_entity)
            impacted_bullets.add(bullet_entity)
            world.delete_entity(bullet_entity)
            world.delete_entity(object_entity)
            break
