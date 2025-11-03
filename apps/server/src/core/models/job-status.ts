export enum JobStatus {
  DOWNLOADING = 'downloading',
  CONVERTING = 'converting',
  TRANSCRIBING = 'transcribing',
  POSTPROCESSING = 'postprocessing',
  PENDING_CONFIRMATION = 'pending_confirmation',
  CONFIRMED = 'confirmed',
  REJECTED = 'rejected',
  FAILED = 'failed',
}
