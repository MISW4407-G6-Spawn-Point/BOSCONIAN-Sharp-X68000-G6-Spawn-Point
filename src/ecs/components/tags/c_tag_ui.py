class CTagUI:
    """Elemento de interfaz: se dibuja encima del juego y no tiembla.
    layer: orden de dibujo (mayor = mas arriba)."""

    def __init__(self, layer:int = 0) -> None:
        self.layer = layer
