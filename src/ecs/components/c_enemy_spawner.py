class CEnemySpawner:
    """Genera enemigos cada cierto tiempo segun la condicion de alerta"""

    def __init__(self, spawn_cfg:dict) -> None:
        self.interval = spawn_cfg["interval"]
        self.max_enemies = spawn_cfg["max_enemies"]
        self.accuracy = spawn_cfg["accuracy"]
        self.weights = spawn_cfg["weights"]
        self.timer = 0.0