class CLifetime:
    """Tiempo que le queda a la entidad antes de borrarse"""

    def __init__(self, time:float) -> None:
        self.time_left = time
