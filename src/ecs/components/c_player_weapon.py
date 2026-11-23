class CPlayerWeapon:
    """Arma del jugador segun el nivel.
    special_shot: dispara 3 balas al frente y 1 atras (en vez de 1 y 1)"""

    def __init__(self, special_shot:bool) -> None:
        self.special_shot = special_shot
