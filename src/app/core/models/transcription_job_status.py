from enum import Enum


class JobStatus(Enum):
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    POSTPROCESSING = "postprocessing"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    FAILED = "failed"
