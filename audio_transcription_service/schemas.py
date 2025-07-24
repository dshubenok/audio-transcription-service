from pydantic import BaseModel, Field
from typing import Literal


class AudioTask(BaseModel):
    """Задача для обработки аудио"""

    client_id: str
    audio_data: bytes


class TranscriptResult(BaseModel):
    """Результат транскрипции"""

    client_id: str
    text: str
    audio_size: int
    processing_time: float = Field(..., ge=0)
    timestamp: str


class ProcessingError(BaseModel):
    """Ошибка обработки"""

    client_id: str
    error: str
    timestamp: str


class WebSocketMessage(BaseModel):
    """Базовое сообщение WebSocket"""

    type: Literal["status", "transcript", "error"]
    client_id: str


class StatusMessage(WebSocketMessage):
    """Сообщение статуса"""

    type: Literal["status"] = "status"
    data: dict


class TranscriptMessage(WebSocketMessage):
    """Сообщение с транскриптом"""

    type: Literal["transcript"] = "transcript"
    data: dict


class ErrorMessage(WebSocketMessage):
    """Сообщение об ошибке"""

    type: Literal["error"] = "error"
    error: dict
