from src.engine.services.configs_service import ConfigsService
from src.engine.services.fonts_service import FontsService
from src.engine.services.images_service import ImagesService
from src.engine.services.sounds_service import SoundService


class ServiceLocator:
    """Punto unico de acceso a todos los recursos externos del juego."""
    configs_service = ConfigsService()
    fonts_service = FontsService()
    images_service = ImagesService()
    sounds_service = SoundService()
