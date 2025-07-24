import multiprocessing as mp
import time
import logging
from datetime import datetime, timezone
from .schemas import AudioTask, TranscriptResult, ProcessingError

logger = logging.getLogger(__name__)


def audio_processor_worker(input_queue: mp.Queue, output_queue: mp.Queue):
    """Обработчик аудио в отдельном процессе - возвращает mock-транскрипты"""
    logger.info("Audio processor worker запущен")

    while True:
        try:
            # Получаем задачу из очереди
            task_data = input_queue.get()
            if task_data is None:  # Сигнал остановки
                break

            task = AudioTask(**task_data)
            start_time = time.time()

            # Mock-обработка: имитируем распознавание на основе размера аудио
            audio_size = len(task.audio_data)
            processing_time = time.time() - start_time

            # Генерируем mock-транскрипт на основе размера
            from .config import MOCK_TRANSCRIPTS, AUDIO_SIZE_THRESHOLDS

            if audio_size < AUDIO_SIZE_THRESHOLDS["short"]:
                transcript_text = MOCK_TRANSCRIPTS["too_small"]
            elif audio_size < AUDIO_SIZE_THRESHOLDS["medium"]:
                transcript_text = MOCK_TRANSCRIPTS["short"]
            elif audio_size < AUDIO_SIZE_THRESHOLDS["long"]:
                transcript_text = MOCK_TRANSCRIPTS["medium"]
            else:
                transcript_text = MOCK_TRANSCRIPTS["long"]

            result = TranscriptResult(
                client_id=task.client_id,
                text=transcript_text,
                audio_size=audio_size,
                processing_time=round(processing_time, 3),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Отправляем результат в выходную очередь
            output_queue.put(result.model_dump())

        except Exception as e:
            logger.error(f"Ошибка в audio processor: {e}")
            error_result = ProcessingError(
                client_id=task.client_id if "task" in locals() else "unknown",
                error=str(e),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            output_queue.put(error_result.model_dump())


class AudioProcessor:
    """Управление обработчиком аудио в отдельном процессе"""

    def __init__(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.process = None

    def start(self):
        """Запускает обработчик аудио в отдельном процессе"""
        self.process = mp.Process(
            target=audio_processor_worker, args=(self.input_queue, self.output_queue)
        )
        self.process.start()
        logger.info("Audio processor запущен в отдельном процессе")

    def stop(self):
        """Останавливает обработчик аудио"""
        if self.process and self.process.is_alive():
            self.input_queue.put(None)  # Сигнал остановки
            from .config import AUDIO_PROCESSOR_SHUTDOWN_TIMEOUT

            self.process.join(timeout=AUDIO_PROCESSOR_SHUTDOWN_TIMEOUT)
            self.process.terminate()
            logger.info("Audio processor остановлен")

    def is_alive(self):
        """Проверяет, работает ли процесс"""
        return self.process and self.process.is_alive()

    def put_task(self, task: AudioTask):
        """Отправляет задачу в очередь"""
        self.input_queue.put(task.model_dump())

    def get_result(self, timeout: int = None):
        """Получает результат из очереди"""
        from .config import AUDIO_PROCESSOR_TIMEOUT

        if timeout is None:
            timeout = AUDIO_PROCESSOR_TIMEOUT
        return self.output_queue.get(timeout=timeout)
