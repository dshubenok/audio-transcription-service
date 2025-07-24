from fastapi import FastAPI, WebSocket
from .config import logger, SERVER_HOST, SERVER_PORT, SERVER_LOG_LEVEL
from .audio_processor import AudioProcessor
from .websocket_manager import ConnectionManager, WebSocketHandler

# Инициализация FastAPI приложения
app = FastAPI(title="Audio Transcription Service")

# Создаем экземпляры компонентов
connection_manager = ConnectionManager()
audio_processor = AudioProcessor()
websocket_handler = WebSocketHandler(connection_manager, audio_processor)


@app.on_event("startup")
async def startup_event():
    """Запуск при старте приложения"""
    audio_processor.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Остановка при завершении приложения"""
    audio_processor.stop()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для обработки аудио"""
    await websocket_handler.handle_connection(websocket)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "WebSocket Audio Transcription Service",
        "version": "1.0.0",
        "description": "Принимает бинарные аудио-чанки, обрабатывает в отдельном процессе, возвращает mock-транскрипты",
        "websocket": "/ws",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "clients": len(connection_manager.active_connections),
        "audio_processor": audio_processor.is_alive(),
    }


def main():
    """Точка входа для CLI команды"""
    import uvicorn

    logger.info("Запуск WebSocket Audio Transcription Service...")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level=SERVER_LOG_LEVEL)


if __name__ == "__main__":
    main()
