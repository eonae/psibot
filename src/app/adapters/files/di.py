from src.app.config import Config

from .local_file_storage import LocalFileStorage

config = Config()

storage = LocalFileStorage(config.AUDIO_DIR)

__all__ = ["storage"]
