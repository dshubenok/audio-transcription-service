# Audio Transcription Service

WebSocket сервис для обработки аудио с FastAPI + Multiprocessing + IPC.

## Быстрый старт

```bash
# Установка
uv sync

# Запуск сервера
uv run serve

# Тестирование
uv run python test_client.py
```

## API

- **WebSocket**: `ws://localhost:8000/ws`
- **Документация**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/health`

## Входные данные

- Бинарные WebSocket сообщения с аудио

## Выходные данные

```json
{
  "type": "transcript",
  "client_id": "client_123",
  "data": {
    "text": "Распознанный текст",
    "audio_size": 8000,
    "processing_time": 0.003,
    "timestamp": "2025-07-24T20:24:26.113Z"
  }
}
```
