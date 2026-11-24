class CIntroTimeline:
    """Linea de tiempo del intro: pasos de interface.json ordenados por start_time.
    named guarda las entidades con "id" para que pasos posteriores las muevan"""

    def __init__(self, steps: list) -> None:
        self.steps = sorted(steps, key=lambda step: step["start_time"])
        self.time = 0.0
        self.next_step = 0
        self.named = {}
