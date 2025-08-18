"""
Адаптеры для внешних сервисов (Redis, DuckDB).
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import duckdb
import redis.asyncio as redis

from .settings import settings

logger = logging.getLogger(__name__)


class RedisAdapter:
    """Адаптер для Redis Pub/Sub."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.connected = False

    async def connect(self) -> bool:
        """Подключение к Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password or None,
                decode_responses=True,
            )

            # Проверяем подключение
            await self.redis_client.ping()
            self.connected = True
            logger.info("✅ Redis подключен успешно")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Отключение от Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
            logger.info("Redis отключен")

    async def publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Публикация события в Redis."""
        if not self.connected or not self.redis_client:
            return False

        try:
            event = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }

            await self.redis_client.publish(settings.redis_channel, json.dumps(event))
            return True

        except Exception as e:
            logger.error(f"Ошибка публикации события: {e}")
            return False

    async def subscribe_to_events(self, callback):
        """Подписка на события из Redis."""
        if not self.connected or not self.redis_client:
            return False

        try:
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(settings.redis_channel)

            async def listen():
                try:
                    if self.pubsub:  # Проверяем, что pubsub не None
                        async for message in self.pubsub.listen():
                            if message["type"] == "message":
                                try:
                                    event = json.loads(message["data"])
                                    await callback(event)
                                except json.JSONDecodeError as e:
                                    logger.error(f"Ошибка парсинга события: {e}")
                except Exception as e:
                    logger.error(f"Ошибка в Redis listener: {e}")

            asyncio.create_task(listen())
            return True

        except Exception as e:
            logger.error(f"Ошибка подписки на события: {e}")
            return False


class DuckDBAdapter:
    """Адаптер для DuckDB (чтение снапшотов)."""

    def __init__(self):
        # Проверяем, что DATA_DIR не None
        if settings.DATA_DIR is None:
            raise ValueError("DATA_DIR не настроен в settings")
        self.db_path = settings.DATA_DIR / "brainzzz.duckdb"
        self.connected = False

    def connect(self) -> bool:
        """Подключение к DuckDB."""
        try:
            # Создаем подключение к DuckDB
            self.connection = duckdb.connect(str(self.db_path))
            self.connected = True
            logger.info("✅ DuckDB подключен успешно")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к DuckDB: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Отключение от DuckDB."""
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
            self.connected = False
            logger.info("DuckDB отключен")

    def get_population_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает снапшоты популяции из DuckDB."""
        if not self.connected:
            return []

        try:
            # Простой запрос для получения данных
            query = """
                SELECT * FROM population_snapshots
                ORDER BY timestamp DESC
                LIMIT ?
            """
            result = self.connection.execute(query, [limit]).fetchall()

            # Преобразуем в список словарей
            snapshots = []
            for row in result:
                snapshots.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "population_size": row[2],
                        "avg_fitness": row[3],
                        "max_fitness": row[4],
                    }
                )

            return snapshots

        except Exception as e:
            logger.error(f"Ошибка получения снапшотов: {e}")
            return []

    def __repr__(self):
        return f"DuckDBAdapter(connected={self.connected})"


# Создаем глобальные экземпляры адаптеров
redis_adapter = RedisAdapter()
duckdb_adapter = DuckDBAdapter()
