import json
import os
import sys


class SaveService:
    """Guarda el puntaje maximo entre ejecuciones.
    Escritorio: archivo JSON. Web (pygbag): localStorage del navegador."""

    def _settings(self) -> dict:
        from src.engine.service_locator import ServiceLocator
        return ServiceLocator.configs_service.get("assets/cfg/game.json")

    def load_hi_score(self, default:int) -> int:
        try:
            if sys.platform == "emscripten":
                import platform
                raw = platform.window.localStorage.getItem(self._settings()["save_key"])
                return int(raw) if raw else default
            with open(self._settings()["save_file"], encoding="utf-8") as save_file:
                return int(json.load(save_file)["hi_score"])
        except Exception:
            return default

    def save_hi_score(self, value:int) -> None:
        try:
            if sys.platform == "emscripten":
                import platform
                platform.window.localStorage.setItem(self._settings()["save_key"], str(value))
                return
            path = self._settings()["save_file"]
            folder = os.path.dirname(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf-8") as save_file:
                json.dump({"hi_score": value}, save_file)
        except Exception:
            pass
