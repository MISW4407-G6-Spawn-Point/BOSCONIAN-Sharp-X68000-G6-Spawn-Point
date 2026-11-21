class CTimedSpawner:
    """Temporizador generico para eventos del nivel (formaciones, espia).
    kind: que se genera. chance: probabilidad de que ocurra cuando se cumple el tiempo."""

    def __init__(self, kind:str, interval:float, chance:float = 1.0) -> None:
        self.kind = kind
        self.interval = interval
        self.chance = chance
        self.timer = 0.0