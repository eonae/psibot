from yandex_cloud_ml_sdk import YCloudML  # type: ignore
from yandex_cloud_ml_sdk.auth import APIKeyAuth

from src.app.core.ports.ml.gpt import Gpt  # type: ignore


class YandexGPT(Gpt):
    def __init__(self, api_key: str, folder_id: str):
        self.sdk = YCloudML(
            folder_id=folder_id,
            auth=APIKeyAuth(api_key=api_key),
        )

        self.model = self.sdk.models.completions("yandexgpt")
        self.model.configure(temperature=0)

    def reply(self, prompt: str) -> str:
        response = self.model.run(prompt)
        return response.text

    @property
    def MAX_SYMBOLS(self) -> int:
        # Из расчёта до 8192 токенов - определено экспериментально
        return 10000
