class CMineBlast:
    """Explosion de mina recien creada: mata lo que este dentro de radius (una sola vez)"""

    def __init__(self, radius:float) -> None:
        self.radius = radius
