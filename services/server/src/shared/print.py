import json
from typing import Any


def pretty_print(data: Any) -> None:
    """Красиво печатает словарь или список с отступами"""
    print(json.dumps(data, indent=2, ensure_ascii=False))
