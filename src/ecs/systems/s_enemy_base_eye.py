import esper

from src.ecs.components.c_enemy_base_eye import CEnemyBaseEye
from src.ecs.components.c_enemy_base_combat import CEnemyBaseCombat
from src.ecs.components.c_surface import CSurface


def system_enemy_base_eye(world: esper.World, delta_time: float) -> None:
    for entity, (surface, eye, combat) in world.get_components(
        CSurface,
        CEnemyBaseEye,
        CEnemyBaseCombat,
    ):
        eye.elapsed_time += delta_time
        current_frame = eye.frame_order[eye.frame_position]
        frame_interval = eye.interval
        if current_frame == 0:
            frame_interval += eye.open_interval_bonus
        if eye.elapsed_time < frame_interval:
            continue

        eye.elapsed_time -= frame_interval
        eye.frame_position = (eye.frame_position + 1) % len(eye.frame_order)
        frame_index = eye.frame_order[eye.frame_position]
        combat.eye_frame_index = frame_index
        surface.surf = combat.compose()
        surface.area = surface.surf.get_rect()
