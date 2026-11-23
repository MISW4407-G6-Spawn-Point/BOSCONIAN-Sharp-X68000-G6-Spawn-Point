import random


class CBaseTurrets:
    """Torretas de una base enemiga: un temporizador por nodo.
    Arrancan al azar para que no disparen todas al tiempo."""

    def __init__(self, count:int, interval_min:float, interval_max:float) -> None:
        self.interval_min = interval_min
        self.interval_max = interval_max
        self.timers = [random.uniform(interval_min, interval_max) for _ in range(count)]
