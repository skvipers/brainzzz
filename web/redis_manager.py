"""
Redis менеджер для работы с событиями Brainzzz.
"""

import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import redis.asyncio as redis

from .settings import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Менеджер Redis для работы с событиями."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_connected = False
        self.event_handlers: Dict[str, Callable] = {}

    async def connect(self) -> bool:
        """Подключается к Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Проверяем соединение
            await self.redis_client.ping()
            self.is_connected = True

            # Создаем pubsub
            self.pubsub = self.redis_client.pubsub()

            logger.info("✅ Redis подключен успешно")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Отключается от Redis."""
        try:
            if self.pubsub:
                await self.pubsub.close()
            if self.redis_client:
                await self.redis_client.close()
            self.is_connected = False
            logger.info("🔌 Redis отключен")
        except Exception as e:
            logger.error(f"Ошибка отключения от Redis: {e}")

    async def publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Публикует событие в Redis."""
        if not self.is_connected:
            logger.warning("Redis не подключен, событие не отправлено")
            return False

        try:
            event = {
                "type": event_type,
                "schema": "1.0",
                "ts": datetime.now().isoformat(),
                "data": data,
            }

            channel = f"brainzzz.events.{event_type}"
            await self.redis_client.publish(channel, json.dumps(event))

            logger.debug(f"📡 Событие {event_type} отправлено в {channel}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки события {event_type}: {e}")
            return False

    async def subscribe_to_events(self, event_types: list[str], handler: Callable):
        """Подписывается на события."""
        if not self.is_connected or not self.pubsub:
            logger.warning("Redis не подключен, подписка невозможна")
            return False

        try:
            # Подписываемся на каналы
            channels = [f"brainzzz.events.{event_type}" for event_type in event_types]
            await self.pubsub.subscribe(*channels)

            # Сохраняем обработчик
            for event_type in event_types:
                self.event_handlers[event_type] = handler

            logger.info(f"📡 Подписка на события: {event_types}")
            return True

        except Exception as e:
            logger.error(f"Ошибка подписки на события: {e}")
            return False

    async def listen_for_events(self):
        """Слушает события из Redis."""
        if not self.is_connected or not self.pubsub:
            return

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        event_type = event_data.get("type")

                        if event_type in self.event_handlers:
                            handler = self.event_handlers[event_type]
                            await handler(event_data)
                        else:
                            logger.debug(f"Неизвестный тип события: {event_type}")

                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {e}")
                    except Exception as e:
                        logger.error(f"Ошибка обработки события: {e}")

        except Exception as e:
            logger.error(f"Ошибка прослушивания событий: {e}")

    async def publish_population_update(self, population_data: Dict[str, Any]):
        """Публикует обновление популяции."""
        return await self.publish_event("population_update", population_data)

    async def publish_brain_evolution(
        self, brain_id: int, evolution_data: Dict[str, Any]
    ):
        """Публикует эволюцию мозга."""
        data = {"brain_id": brain_id, **evolution_data}
        return await self.publish_event("brain_evolution", data)

    async def publish_task_completion(self, task_name: str, results: Dict[str, Any]):
        """Публикует завершение задачи."""
        data = {"task_name": task_name, **results}
        return await self.publish_event("task_completion", data)

    async def publish_system_status(self, status_data: Dict[str, Any]):
        """Публикует статус системы."""
        return await self.publish_event("system_status", status_data)

    async def get_system_stats(self) -> Dict[str, Any]:
        """Получает статистику системы."""
        if not self.is_connected:
            return {}

        try:
            stats = await self.redis_client.info()
            return {
                "redis_version": stats.get("redis_version"),
                "connected_clients": stats.get("connected_clients"),
                "used_memory_human": stats.get("used_memory_human"),
                "total_commands_processed": stats.get("total_commands_processed"),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики Redis: {e}")
            return {}


# Глобальный экземпляр Redis менеджера
redis_manager = RedisManager()
