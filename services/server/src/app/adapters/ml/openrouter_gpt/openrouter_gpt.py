"""
Реализация GPT на основе сервисаOpenRouter.
"""

from openai import OpenAI  # type: ignore

from src.app.core.ports.ml.gpt import Gpt  # type: ignore


class OpenRouterGPT(Gpt):
    """
    OpenRouter GPT.
    """

    def __init__(self, api_key: str, model: str):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def reply(self, prompt: str) -> str:

        completion = self.client.chat.completions.create(
            model=self.model,  # type: ignore
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        response = completion.choices[0].message.content
        assert response is not None
        return response

    @property
    def MAX_SYMBOLS(self) -> int:
        # Из расчёта до 8192 токенов - определено экспериментально
        return 10000
