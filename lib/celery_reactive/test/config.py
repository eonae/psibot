import os

from dotenv import load_dotenv

load_dotenv()

_BROKER_URL = os.getenv("CELERY_BROKER_URL")
_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

assert _BROKER_URL is not None
assert _RESULT_BACKEND is not None

BROKER_URL: str = _BROKER_URL
RESULT_BACKEND: str = _RESULT_BACKEND
