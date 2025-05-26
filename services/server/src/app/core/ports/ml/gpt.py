from typing import Protocol


class Gpt(Protocol):
    @property
    def MAX_SYMBOLS(self) -> int:
        ...

    def reply(self, prompt: str) -> str:
        ...
