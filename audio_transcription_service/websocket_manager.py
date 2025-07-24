import json
import uuid
import logging
from fastapi import WebSocket
from .schemas import AudioTask, StatusMessage, ErrorMessage, TranscriptMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Управление WebSocket соединениями"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Принимает новое WebSocket соединение"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Отключает WebSocket соединение"""
        self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        """Отправляет сообщение через WebSocket"""
        await websocket.send_text(json.dumps(message, ensure_ascii=False))


class WebSocketHandler:
    """Обработчик WebSocket сообщений"""

    def __init__(self, connection_manager: ConnectionManager, audio_processor):
        self.connection_manager = connection_manager
        self.audio_processor = audio_processor

    async def handle_connection(self, websocket: WebSocket):
        """Обрабатывает WebSocket соединение"""
        await self.connection_manager.connect(websocket)
        client_id = f"client_{uuid.uuid4().hex[:8]}"

        try:
            # Статус подключения
            status_message = StatusMessage(
                client_id=client_id,
                data={"status": "connected", "message": "Готов к приему аудио"},
            )
            await self.connection_manager.send_message(
                websocket, status_message.model_dump()
            )

            while True:
                # Получаем бинарные аудио-данные
                audio_data = await websocket.receive_bytes()

                # Валидация размера
                from .config import MIN_AUDIO_SIZE

                if len(audio_data) < MIN_AUDIO_SIZE:
                    error_message = ErrorMessage(
                        client_id=client_id,
                        error={
                            "code": "CHUNK_TOO_SMALL",
                            "message": f"Минимум {MIN_AUDIO_SIZE} байт, получено: {len(audio_data)}",
                        },
                    )
                    await self.connection_manager.send_message(
                        websocket, error_message.model_dump()
                    )
                    continue

                # Отправляем в очередь для обработки в отдельном процессе
                task = AudioTask(client_id=client_id, audio_data=audio_data)
                self.audio_processor.put_task(task)

                # Ждем результат из выходной очереди
                try:
                    from .config import WEBSOCKET_TIMEOUT

                    result = self.audio_processor.get_result(timeout=WEBSOCKET_TIMEOUT)

                    if "error" in result:
                        # Ошибка обработки
                        error_message = ErrorMessage(
                            client_id=client_id,
                            error={
                                "code": "PROCESSING_ERROR",
                                "message": result["error"],
                            },
                        )
                        await self.connection_manager.send_message(
                            websocket, error_message.model_dump()
                        )
                    else:
                        # Успешный результат
                        transcript_message = TranscriptMessage(
                            client_id=client_id,
                            data={
                                "text": result["text"],
                                "audio_size": result["audio_size"],
                                "processing_time": result["processing_time"],
                                "timestamp": result["timestamp"],
                                "language": "ru",
                                "duration": result["processing_time"],
                            },
                        )
                        await self.connection_manager.send_message(
                            websocket, transcript_message.model_dump()
                        )

                except Exception as e:
                    # Таймаут или другая ошибка
                    error_message = ErrorMessage(
                        client_id=client_id,
                        error={
                            "code": "TIMEOUT_ERROR",
                            "message": f"Превышено время ожидания: {str(e)}",
                        },
                    )
                    await self.connection_manager.send_message(
                        websocket, error_message.model_dump()
                    )

        except Exception as e:
            logger.error(f"Ошибка в WebSocket соединении: {e}")
        finally:
            self.connection_manager.disconnect(websocket)
            logger.info(f"Клиент {client_id} отключился")
