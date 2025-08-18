"""
WebSocket хаб для ретрансляции событий из Redis в браузер.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Set

from core.adapters import redis_adapter
from core.schemas import MessageType, WebSocketMessage
from core.settings import settings
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketHub:
    """Хаб для управления WebSocket соединениями."""

    def __init__(self, max_connections: int = None):
        self.active_connections: Set[WebSocket] = set()
        self.redis_callback_task = None
        self.max_connections = max_connections or settings.ws_max_connections

    async def connect(self, websocket: WebSocket):
        """Подключение нового WebSocket клиента."""
        client_id = id(websocket)

        # Проверяем лимит соединений
        if len(self.active_connections) >= self.max_connections:
            logger.warning(
                f"❌ Достигнут лимит WebSocket соединений: {self.max_connections}"
            )
            await websocket.close(code=1013, reason="Too many connections")
            return

        # Добавляем задержку для предотвращения race conditions
        await asyncio.sleep(1.0)  # Увеличиваем задержку до 1 секунды

        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            logger.info(
                f"✅ WebSocket #{client_id} подключен. "
                f"Всего: {len(self.active_connections)}"
            )

            # Отправляем приветственное сообщение
            welcome_msg = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={
                    "status": "connected",
                    "message": "Добро пожаловать в Brainzzz!",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            await self.send_personal_message(websocket, welcome_msg)
            logger.info(
                f"📤 Приветственное сообщение отправлено WebSocket #{client_id}"
            )

        except Exception as e:
            logger.error(f"❌ Ошибка подключения WebSocket #{client_id}: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            try:
                await websocket.close(code=1011, reason="Internal error")
            except Exception:
                pass

    def disconnect(self, websocket: WebSocket):
        """Отключение WebSocket клиента."""
        client_id = id(websocket)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"🔌 WebSocket #{client_id} отключен. "
                f"Всего: {len(self.active_connections)}"
            )
        else:
            logger.debug(f"🔌 WebSocket #{client_id} уже отключен")

    async def send_personal_message(
        self, websocket: WebSocket, message: WebSocketMessage
    ):
        """Отправка личного сообщения клиенту."""
        try:
            await websocket.send_text(message.json())
        except Exception as e:
            logger.error(f"Ошибка отправки личного сообщения: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: WebSocketMessage):
        """Отправка сообщения всем подключенным клиентам."""
        if not self.active_connections:
            return

        # Создаем копию множества для безопасной итерации
        connections = self.active_connections.copy()

        for connection in connections:
            try:
                await connection.send_text(message.json())
            except Exception as e:
                logger.error(f"Ошибка broadcast: {e}")
                self.disconnect(connection)

    async def start_redis_listener(self):
        """Запуск слушателя Redis событий."""
        if self.redis_callback_task:
            return

        try:
            # Подключаемся к Redis
            await redis_adapter.connect()

            # Подписываемся на события
            success = await redis_adapter.subscribe_to_events(self._handle_redis_event)
            if success:
                logger.info("✅ Redis listener запущен")
            else:
                logger.error("❌ Не удалось запустить Redis listener")

        except Exception as e:
            logger.error(f"❌ Ошибка запуска Redis listener: {e}")

    async def stop_redis_listener(self):
        """Остановка слушателя Redis событий."""
        if self.redis_callback_task:
            self.redis_callback_task.cancel()
            self.redis_callback_task = None

        await redis_adapter.disconnect()
        logger.info("Redis listener остановлен")

    async def _handle_redis_event(self, event: Dict[str, Any]):
        """Обработчик событий из Redis."""
        try:
            # Создаем WebSocket сообщение
            message = WebSocketMessage(
                type=event.get("type", "unknown"),
                data=event.get("data", {}),
                ts=datetime.now(),
            )

            # Отправляем всем подключенным клиентам
            await self.broadcast(message)

        except Exception as e:
            logger.error(f"Ошибка обработки Redis события: {e}")

    async def cleanup_dead_connections(self):
        """Очистка мертвых WebSocket соединений."""
        dead_connections = set()

        for connection in self.active_connections:
            try:
                # Проверяем, что соединение еще живо
                await connection.ping()
            except Exception:
                dead_connections.add(connection)

        # Удаляем мертвые соединения
        for dead_connection in dead_connections:
            self.disconnect(dead_connection)

        if dead_connections:
            logger.info(f"🧹 Очищено {len(dead_connections)} мертвых соединений")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Возвращает статистику соединений."""
        return {
            "total_connections": len(self.active_connections),
            "max_connections": self.max_connections,
            "available_connections": self.max_connections
            - len(self.active_connections),
            "can_accept": len(self.active_connections) < self.max_connections,
        }

    def __repr__(self):
        return (
            f"WebSocketHub(connections={len(self.active_connections)}/"
            f"{self.max_connections})"
        )
