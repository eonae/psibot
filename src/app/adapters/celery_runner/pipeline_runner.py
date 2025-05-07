from uuid import UUID

from celery import chain, chord  # type: ignore

from src.app.core.ports import PipelineRunner
from .singleton import celery_app


class CeleryRunner(PipelineRunner):
    _download_task = celery_app.tasks["download"]
    _convert_task = celery_app.tasks["convert"]
    _diarize_task = celery_app.tasks["diarize"]
    _transcribe_task = celery_app.tasks["transcribe"]
    _merge_task = celery_app.tasks["merge"]
    _postprocess_task = celery_app.tasks["postprocess"]

    def run_pipeline(self, job_id: UUID) -> None:
        pipeline = chain(
            self._download_task.s(str(job_id)),
            self._convert_task.s(),
            chord(
                [
                    self._diarize_task.s(),
                    self._transcribe_task.s(),
                ],
                self._merge_task.s()
            ),
            self._postprocess_task.s(),
        )

        pipeline.apply_async()
