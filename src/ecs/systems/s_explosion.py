import esper
from src.ecs.components.c_explosion import CExplosion
from src.ecs.components.c_surface import CSurface


def system_explosion(world: esper.World, delta_time: float) -> None:
    for entity, (explosion, surface) in world.get_components(
        CExplosion,
        CSurface,
    ):
        explosion.elapsed_time += delta_time
        while explosion.elapsed_time >= explosion.frame_duration:
            explosion.elapsed_time -= explosion.frame_duration
            explosion.frame_index += 1
            if explosion.frame_index >= len(explosion.frames):
                world.delete_entity(entity)
                break
            surface.surf = explosion.frames[explosion.frame_index]
            surface.area = surface.surf.get_rect()
