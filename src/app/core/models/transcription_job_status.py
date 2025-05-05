from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    CONVERTING = "converting"
    DIARIZING = "diarizing"
    TRANSCRIBING = "transcribing"
    MERGING = "merging"
    POSTPROCESSING = "postprocessing"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    FAILED = "failed"
