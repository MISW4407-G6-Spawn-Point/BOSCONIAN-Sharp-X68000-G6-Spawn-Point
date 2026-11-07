import json


class ConfigsService:
    """Carga y guarda en cache los archivos de configuracion .json del juego."""

    def __init__(self) -> None:
        self._configs = {}

    def get(self, path: str) -> dict:
        if path not in self._configs:
            with open(path, encoding="utf-8") as config_file:
                self._configs[path] = json.load(config_file)
        return self._configs[path]
