import esper

from src.ecs.components.c_sprite_animation import CSpriteAnimation
from src.ecs.components.c_surface import CSurface


def system_sprite_animation(world: esper.World, delta_time: float) -> None:
    for _, (surface, animation) in world.get_components(
        CSurface,
        CSpriteAnimation,
    ):
        animation.elapsed_time += delta_time
        if animation.elapsed_time < animation.frame_duration:
            continue

        animation.elapsed_time -= animation.frame_duration
        animation.frame_index = (animation.frame_index + 1) % len(animation.frames)
        surface.surf = animation.frames[animation.frame_index]
        surface.area = surface.surf.get_rect()
