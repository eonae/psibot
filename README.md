# SpeechKit

Приложение для создания протоколов психологических сессий.

## Установка

### Системные требования

- Python 3.9 или выше
- Poetry 2.0+ для управления зависимостями
- macOS (протестировано на macOS Sonoma)

### Системные зависимости

Для успешной установки необходимо установить следующие системные зависимости через Homebrew:

```bash
# Установка cmake (система сборки)
brew install cmake

# Установка sentencepiece (библиотека для обработки текста)
brew install sentencepiece

# Установка protobuf (необходим для sentencepiece)
brew install protobuf
```

### Установка Python-зависимостей

После установки системных зависимостей, установите Python-пакеты с помощью Poetry:

```bash
# Активация виртуального окружения
poetry env use python

# Установка зависимостей
poetry install
```

### Hugging Face токен

Для работы с pyannote-audio требуется токен от Hugging Face. Вы можете получить его на сайте [Hugging Face](https://huggingface.co/). 

Создайте файл `.env` в корне проекта и добавьте в него:
```
HUGGING_FACE_TOKEN=ваш_токен
```

### Доступ к моделям

Перед использованием приложения необходимо получить доступ к следующим моделям на Hugging Face:

1. [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization)
2. [pyannote/segmentation](https://huggingface.co/pyannote/segmentation)

Для каждой модели:
1. Перейдите по ссылке
2. Нажмите "Access repository"
3. Примите условия использования

## Использование

1. Поместите аудио файл в директорию `audio/src/` с именем `session_1m_1` (любое расширение)
2. Запустите приложение:
```bash
poetry run start
```

Приложение автоматически:
- Создаст необходимые директории
- Конвертирует аудио в WAV формат (если нужно)
- Выполнит диаризацию 