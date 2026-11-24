class CDemoPilot:
    """IA de la demo: cada turn_interval apunta a la base mas cercana,
    esquiva lo que tenga a menos de avoid_distance adelante y dispara cada fire_interval"""

    def __init__(self, turn_interval: float, fire_interval: float, avoid_distance: float) -> None:
        self.turn_interval = turn_interval
        self.fire_interval = fire_interval
        self.avoid_distance = avoid_distance
        self.turn_timer = 0.0
        self.fire_timer = 0.0
