"""Модуль для работы с вычислительными устройствами"""

import torch  # type: ignore


def get_device():
    """Определяет оптимальное устройство для вычислений"""
    if torch.backends.mps.is_available():
        return torch.device("mps")  # Apple Silicon GPU

    if torch.cuda.is_available():
        return torch.device("cuda")  # NVIDIA GPU

    return torch.device("cpu")  # CPU
