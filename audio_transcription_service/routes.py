from fastapi import APIRouter, WebSocket
from .websocket_manager import WebSocketHandler

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, handler: WebSocketHandler):
    """WebSocket endpoint для обработки аудио"""
    await handler.handle_connection(websocket)


@router.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "WebSocket Audio Transcription Service",
        "version": "1.0.0",
        "description": "Принимает бинарные аудио-чанки, обрабатывает в отдельном процессе, возвращает mock-транскрипты",
        "websocket": "/ws",
        "docs": "/docs",
    }


@router.get("/health")
async def health(connection_manager, audio_processor):
    """Health check endpoint"""
    return {
        "status": "ok",
        "clients": len(connection_manager.active_connections),
        "audio_processor": audio_processor.is_alive(),
    }
