from lib.celery_reactive.test.app import app


@app.task(bind=True)
def add(self, a: int, b: int) -> int:
    """Суммирует два числа"""

    # Метаданные доступны через self.request
    print(f"Job ID из хедеров: {self.request.headers.get('job_id')}")
    return a + b
