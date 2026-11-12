import math
import esper
import pygame

from src.ecs.components.c_player_ship import CPlayerShip
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

DIRECTIONS = [pygame.Vector2(0, -1).rotate(45 * i) for i in range(8)]


def _input_to_index(vec:pygame.Vector2) -> int:
    angle = math.degrees(math.atan2(vec.x, -vec.y)) % 360
    return round(angle / 45) % 8


def system_player_ship(world:esper.World, delta_time:float):
    components = world.get_components(CTransform, CVelocity, CSurface, CPlayerShip)

    c_t:CTransform
    c_v:CVelocity
    c_s:CSurface
    c_p:CPlayerShip
    for _, (c_t, c_v, c_s, c_p) in components:
        if c_p.input.length_squared() > 0:
            new_index = _input_to_index(c_p.input)
            if new_index != c_p.dir_index:
                center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
                c_p.dir_index = new_index
                c_s.surf = c_p.sprites[new_index]
                c_s.area = c_s.surf.get_rect()
                c_t.pos = center - pygame.Vector2(c_s.area.size) / 2

        #siempre avanza, acelerando suave hasta la maxima
        c_p.speed = min(c_p.max_speed, c_p.speed + c_p.acceleration * delta_time)
        c_v.vel = DIRECTIONS[c_p.dir_index] * c_p.speed