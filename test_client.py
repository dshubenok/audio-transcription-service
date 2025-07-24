import asyncio
import websockets
import json
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)


def generate_test_audio(size: int) -> bytes:
    """Генерирует тестовые аудио данные"""
    return bytes([random.randint(0, 255) for _ in range(size)])


async def test_client():
    """Тестовый клиент"""
    uri = "ws://localhost:8000/ws"

    try:
        logger.info(f"Подключение к {uri}...")

        async with websockets.connect(uri) as websocket:
            logger.info("Подключен к FastAPI серверу")

            async def listen():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)

                        if data["type"] == "transcript":
                            text = data["data"]["text"]
                            lang = data["data"].get("language", "unknown")
                            duration = data["data"].get("duration", 0)
                            logger.info(f"Распознано [{lang}]: {text} ({duration}s)")
                        elif data["type"] == "error":
                            error = data["error"]["message"]
                            logger.error(f"Ошибка: {error}")
                        else:
                            logger.info(f"Получено: {data}")

                except websockets.exceptions.ConnectionClosed:
                    logger.info("Соединение закрыто")
                except Exception as e:
                    logger.error(f"Ошибка чтения: {e}")

            listen_task = asyncio.create_task(listen())

            # Тестируем разные размеры
            test_sizes = [500, 1500, 3000, 8000]

            for i, size in enumerate(test_sizes, 1):
                logger.info(f"Отправка аудио чанка {i} размером {size} байт...")
                audio_data = generate_test_audio(size)

                await websocket.send(audio_data)
                await asyncio.sleep(3)

            logger.info("Ждем последние ответы...")
            await asyncio.sleep(5)
            listen_task.cancel()

    except websockets.exceptions.ConnectionRefused:
        logger.error("Не удалось подключиться к серверу")
    except Exception as e:
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    logger.info("Тестовый клиент для FastAPI Audio Transcription Service")
    logger.info("=" * 60)
    asyncio.run(test_client())
