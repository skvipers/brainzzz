"""
Адаптеры для внешних сервисов (Redis, DuckDB).
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import redis.asyncio as redis
import duckdb
from pathlib import Path

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
                decode_responses=True
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
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis_client.publish(
                settings.redis_channel,
                json.dumps(event)
            )
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
        self.db_path = settings.DATA_DIR / "brainzzz.duckdb"
        self.connected = False
    
    def connect(self) -> bool:
        """Подключение к DuckDB."""
        try:
            # Создаем файл если его нет
            self.db_path.parent.mkdir(exist_ok=True)
            
            # Подключаемся и создаем таблицы если их нет
            with duckdb.connect(str(self.db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS population_snapshots (
                        id INTEGER PRIMARY KEY,
                        generation INTEGER,
                        population_size INTEGER,
                        avg_fitness REAL,
                        max_fitness REAL,
                        timestamp TIMESTAMP,
                        data TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS brain_snapshots (
                        id INTEGER PRIMARY KEY,
                        brain_id TEXT,
                        generation INTEGER,
                        fitness REAL,
                        nodes INTEGER,
                        connections INTEGER,
                        timestamp TIMESTAMP,
                        data TEXT
                    )
                """)
            
            self.connected = True
            logger.info("✅ DuckDB подключен успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к DuckDB: {e}")
            self.connected = False
            return False
    
    def get_population_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение снапшотов популяции."""
        if not self.connected:
            return []
        
        try:
            with duckdb.connect(str(self.db_path)) as conn:
                result = conn.execute("""
                    SELECT * FROM population_snapshots 
                    ORDER BY generation DESC 
                    LIMIT ?
                """, [limit]).fetchall()
                
                columns = [desc[0] for desc in conn.description]
                return [dict(zip(columns, row)) for row in result]
                
        except Exception as e:
            logger.error(f"Ошибка чтения снапшотов популяции: {e}")
            return []
    
    def get_brain_snapshots(self, brain_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение снапшотов мозга."""
        if not self.connected:
            return []
        
        try:
            with duckdb.connect(str(self.db_path)) as conn:
                if brain_id:
                    result = conn.execute("""
                        SELECT * FROM brain_snapshots 
                        WHERE brain_id = ? 
                        ORDER BY generation DESC 
                        LIMIT ?
                    """, [brain_id, limit]).fetchall()
                else:
                    result = conn.execute("""
                        SELECT * FROM brain_snapshots 
                        ORDER BY generation DESC 
                        LIMIT ?
                    """, [limit]).fetchall()
                
                columns = [desc[0] for desc in conn.description]
                return [dict(zip(columns, row)) for row in result]
                
        except Exception as e:
            logger.error(f"Ошибка чтения снапшотов мозга: {e}")
            return []


# Создаем экземпляры адаптеров
redis_adapter = RedisAdapter()
duckdb_adapter = DuckDBAdapter() 