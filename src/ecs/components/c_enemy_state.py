from enum import Enum
import pygame


class CEnemyState:
    """Patron State para la IA de los enemigos I, P y E.
    heading: direccion actual (vector unitario). Se gira hacia el objetivo
    como maximo turn_rate grados por segundo (steering)."""

    def __init__(self, enemy_cfg:dict, sprites:list, heading:pygame.Vector2,
                 speed:float, accuracy:float) -> None:
        self.sprites = sprites
        self.heading = heading
        self.speed = speed
        self.turn_rate = enemy_cfg["turn_rate"] * accuracy
        self.chase_time = enemy_cfg.get("chase_time", 0)
        self.wander_interval = enemy_cfg.get("wander_interval", 1.0)
        self.timer = 0.0
        self.dir_index = -1
        behaviour = enemy_cfg["behaviour"]
        self.behaviour = behaviour
        self.state = EnemyState.STRAIGHT if behaviour == "straight" else EnemyState.CHASE


class EnemyState(Enum):
    CHASE = 0      # persigue al jugador
    LEAVE = 1      # tipo I: deja de perseguir y se va derecho
    WANDER = 2     # tipo P: cambia de direccion al azar
    STRAIGHT = 3   # tipo E: va derecho sin desviarse