import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация сервера
SERVER_HOST = "localhost"
SERVER_PORT = 8000
SERVER_LOG_LEVEL = "info"

# Конфигурация WebSocket
MIN_AUDIO_SIZE = 100  # байт
WEBSOCKET_TIMEOUT = 10  # секунд

# Конфигурация Audio Processor
AUDIO_PROCESSOR_TIMEOUT = 10  # секунд
AUDIO_PROCESSOR_SHUTDOWN_TIMEOUT = 5  # секунд

# Mock-транскрипты настройки
MOCK_TRANSCRIPTS = {
    "too_small": "Аудио слишком короткое для распознавания",
    "short": "Короткое сообщение: привет мир",
    "medium": "Среднее сообщение: это тестовое аудио для распознавания речи",
    "long": "Длинное сообщение: система успешно обработала большой аудиофайл и готова к работе",
}

# Пороги размеров для mock-транскриптов
AUDIO_SIZE_THRESHOLDS = {
    "short": 1000,
    "medium": 5000,
    "long": 15000,
}
