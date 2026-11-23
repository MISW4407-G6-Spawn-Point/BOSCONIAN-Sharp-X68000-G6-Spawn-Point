class CLaunchedBy:
    """Enemigo recien lanzado por el nucleo de una base: no rebota contra ella
    hasta salir de su area"""

    def __init__(self, base_entity:int) -> None:
        self.base_entity = base_entity
