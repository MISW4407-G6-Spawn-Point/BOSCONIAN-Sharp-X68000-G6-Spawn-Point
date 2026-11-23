class CBaseCore:
    """Nucleo de una base enemiga.
    mode: "open" (siempre abierto, no lanza) o "cycle" (abre, cierra y lanza un E al abrir)
    launched: ya lanzo en la apertura actual"""

    def __init__(self, mode:str) -> None:
        self.mode = mode
        self.launched = False
