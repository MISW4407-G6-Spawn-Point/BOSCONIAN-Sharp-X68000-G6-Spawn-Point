from enum import Enum


class CPlayerState:
    """Patron State del jugador: vivo o muerto esperar respawn"""

    def __init__(self, respawn_time:float) -> None:
        self.state = PlayerState.ALIVE
        self.respawn_time = respawn_time
        self.timer = 0.0


class PlayerState(Enum):
    ALIVE = 0
    DEAD = 1