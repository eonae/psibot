from typing import Protocol
from uuid import UUID


class PipelineRunner(Protocol):
    def run_pipeline(self, job_id: UUID) -> None:
        ...
