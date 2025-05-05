from pathlib import Path

from src.app.adapters.files import storage
from src.app.adapters.ml import YandexGPT
from src.app.config import Config
from src.app.core.services import PostprocessingService


def postprocess_results_task(source_filename: str, target_filename: str) -> None:
    config = Config()
    gpt = YandexGPT(
        api_key=config.YC_API_KEY,
        folder_id=config.YC_FOLDER_ID,
    )

    postprocessing_service = PostprocessingService(storage, gpt)
    postprocessing_service.postprocess(Path(source_filename), Path(target_filename))
