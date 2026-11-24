class CSpecialPower:
    """BOOST (tecla X): cargas, tiempo activo, cooldown y velocidad normal de la nave."""

    def __init__(self, charges: int, max_charges: int, normal_speed: float) -> None:
        self.charges = charges
        self.max_charges = max_charges
        self.normal_speed = normal_speed
        self.time_left = 0.0
        self.cooldown_left = 0.0
        self.trail_timer = 0.0
