"""
FastAPI приложение.
"""

from fastapi import FastAPI, HTTPException, UploadFile  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from src.app.adapters.celery_runner import CeleryRunner
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.models.input_file_dto import DownloadedFileDTO
from src.app.core.use_cases import HandleNewFileUseCase

app = FastAPI(title="SpeechKit API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация зависимостей
notifier = TelegramNotifier(bot)
jobs_repository = make_jobs_repository()
pipeline_runner = CeleryRunner()

handle_new_file = HandleNewFileUseCase(
    jobs=jobs_repository,
    notifier=notifier,
    storage=storage,
    pipeline_runner=pipeline_runner,
)


@app.post("/upload")
async def upload_file(file: UploadFile, user_id: int):
    """
    Загружает файл и запускает обработку.
    """
    try:
        # Читаем содержимое файла
        content = await file.read()

        # Создаем DTO для обработки
        input_file = DownloadedFileDTO(
            filename=file.filename,
            mime_type=file.content_type,
            size=len(content),
            content=content,
        )

        # Запускаем обработку
        await handle_new_file.execute(user_id, input_file)

        return {"message": "File uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
