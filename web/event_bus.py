"""
Event Bus для интеграции Ray с Redis.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .redis_manager import redis_manager

logger = logging.getLogger(__name__)


class EventBus:
    """Event Bus для интеграции Ray с Redis."""

    def __init__(self):
        self.is_running = False
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_handlers: Dict[str, List[callable]] = {}

    async def start(self):
        """Запускает Event Bus."""
        if self.is_running:
            return

        self.is_running = True
        logger.info("🚀 Event Bus запущен")

        # Запускаем обработчик событий
        asyncio.create_task(self._event_processor())

    async def stop(self):
        """Останавливает Event Bus."""
        self.is_running = False
        logger.info("🛑 Event Bus остановлен")

    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Публикует событие в Event Bus."""
        event = {
            "type": event_type,
            "schema": "1.0",
            "ts": datetime.now().isoformat(),
            "data": data,
        }

        await self.event_queue.put(event)
        logger.debug(f"📡 Событие {event_type} добавлено в очередь")

    def subscribe(self, event_type: str, handler: callable):
        """Подписывается на события."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.debug(f"📡 Подписка на {event_type}: {handler.__name__}")

    def unsubscribe(self, event_type: str, handler: callable):
        """Отписывается от событий."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                logger.debug(f"📡 Отписка от {event_type}: {handler.__name__}")
            except ValueError:
                pass

    async def _event_processor(self):
        """Обработчик событий из очереди."""
        while self.is_running:
            try:
                # Ждем событие из очереди
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # Обрабатываем событие
                await self._process_event(event)

                # Отмечаем задачу как выполненную
                self.event_queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Ошибка обработки события: {e}")

    async def _process_event(self, event: Dict[str, Any]):
        """Обрабатывает одно событие."""
        event_type = event.get("type")
        event_data = event.get("data", {})

        logger.debug(f"🔍 Обработка события: {event_type}")

        # Вызываем обработчики
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                except Exception as e:
                    logger.error(f"Ошибка в обработчике {handler.__name__}: {e}")

        # Публикуем в Redis
        if redis_manager.is_connected:
            await redis_manager.publish_event(event_type, event_data)

    # Специализированные методы для событий Brainzzz

    async def publish_population_tick(
        self,
        generation: int,
        population_size: int,
        best_fitness: float,
        mean_fitness: float,
    ):
        """Публикует тик популяции."""
        data = {
            "generation": generation,
            "population_size": population_size,
            "best_fitness": best_fitness,
            "mean_fitness": mean_fitness,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("pop_tick", data)

    async def publish_brain_snapshot(self, brain_id: int, brain_data: Dict[str, Any]):
        """Публикует снапшот мозга."""
        data = {
            "brain_id": brain_id,
            "snapshot": brain_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("brain_snapshot", data)

    async def publish_trace_chunk(
        self, generation: int, trace_data: List[Dict[str, Any]]
    ):
        """Публикует чанк трейса."""
        data = {
            "generation": generation,
            "traces": trace_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("trace_chunk", data)

    async def publish_help_score(
        self,
        brain_id: int,
        help_score: float,
        help_type: str,
        target_id: Optional[int] = None,
    ):
        """Публикует help score."""
        data = {
            "brain_id": brain_id,
            "help_score": help_score,
            "help_type": help_type,
            "target_id": target_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("help_score", data)

    async def publish_growth_event(
        self, brain_id: int, growth_type: str, growth_data: Dict[str, Any]
    ):
        """Публикует событие роста."""
        data = {
            "brain_id": brain_id,
            "growth_type": growth_type,
            "growth_data": growth_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("growth", data)

    async def publish_lineage_update(
        self,
        brain_id: int,
        parent_id: Optional[int],
        mutation_type: str,
        fitness_delta: float,
    ):
        """Публикует обновление родословной."""
        data = {
            "brain_id": brain_id,
            "parent_id": parent_id,
            "mutation_type": mutation_type,
            "fitness_delta": fitness_delta,
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("lineage", data)

    async def publish_error(
        self, error_type: str, error_message: str, context: Dict[str, Any] = None
    ):
        """Публикует ошибку."""
        data = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        }
        await self.publish_event("error", data)


# Глобальный экземпляр Event Bus
event_bus = EventBus()
