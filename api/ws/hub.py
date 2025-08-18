"""
WebSocket хаб для ретрансляции событий из Redis в браузер.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from core.schemas import WebSocketMessage, MessageType
from core.adapters import redis_adapter
from core.settings import settings

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
            logger.warning(f"❌ Достигнут лимит WebSocket соединений: {self.max_connections}")
            await websocket.close(code=1013, reason="Too many connections")
            return
        
        # Добавляем задержку для предотвращения race conditions
        await asyncio.sleep(1.0)  # Увеличиваем задержку до 1 секунды
        
        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            logger.info(f"✅ WebSocket #{client_id} подключен. Всего: {len(self.active_connections)}")
            
            # Отправляем приветственное сообщение
            welcome_msg = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={
                    "status": "connected",
                    "message": "Добро пожаловать в Brainzzz!",
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.send_personal_message(websocket, welcome_msg)
            logger.info(f"📤 Приветственное сообщение отправлено WebSocket #{client_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения WebSocket #{client_id}: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            try:
                await websocket.close(code=1011, reason="Internal error")
            except:
                pass
    
    def disconnect(self, websocket: WebSocket):
        """Отключение WebSocket клиента."""
        client_id = id(websocket)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"🔌 WebSocket #{client_id} отключен. Всего: {len(self.active_connections)}")
        else:
            logger.debug(f"🔌 WebSocket #{client_id} уже отключен")
    
    async def send_personal_message(self, websocket: WebSocket, message: WebSocketMessage):
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
        
        async def redis_callback(event: Dict[str, Any]):
            """Обработчик событий из Redis."""
            try:
                event_type = event.get("type")
                event_data = event.get("data", {})
                
                # Создаем WebSocket сообщение
                if event_type == "population_update":
                    message = WebSocketMessage(
                        type=MessageType.POPULATION_UPDATE,
                        data=event_data
                    )
                elif event_type == "brain_update":
                    message = WebSocketMessage(
                        type=MessageType.BRAIN_UPDATE,
                        data=event_data
                    )
                elif event_type == "task_update":
                    message = WebSocketMessage(
                        type=MessageType.TASK_UPDATE,
                        data=event_data
                    )
                elif event_type == "evolution_step":
                    message = WebSocketMessage(
                        type=MessageType.EVOLUTION_STEP,
                        data=event_data
                    )
                else:
                    # Неизвестный тип события
                    message = WebSocketMessage(
                        type=MessageType.SYSTEM_STATUS,
                        data={
                            "event_type": event_type,
                            "data": event_data,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                # Отправляем всем клиентам
                await self.broadcast(message)
                
            except Exception as e:
                logger.error(f"Ошибка обработки Redis события: {e}")
        
        # Подписываемся на Redis события
        success = await redis_adapter.subscribe_to_events(redis_callback)
        if success:
            logger.info("✅ Redis listener запущен")
        else:
            logger.warning("⚠️ Не удалось запустить Redis listener")
    
    async def stop_redis_listener(self):
        """Остановка слушателя Redis событий."""
        if self.redis_callback_task:
            self.redis_callback_task.cancel()
            self.redis_callback_task = None
            logger.info("Redis listener остановлен")
    
    async def cleanup_dead_connections(self):
        """Очистка мертвых WebSocket соединений."""
        dead_connections = set()
        
        for connection in self.active_connections:
            try:
                # Проверяем состояние соединения
                if connection.client_state.value == 3:  # WebSocketState.DISCONNECTED
                    dead_connections.add(connection)
            except Exception:
                dead_connections.add(connection)
        
        # Удаляем мертвые соединения
        for connection in dead_connections:
            self.disconnect(connection)
        
        if dead_connections:
            logger.info(f"Очищено {len(dead_connections)} мертвых соединений")
    
    def get_connection_stats(self):
        """Получение статистики соединений."""
        return {
            "active": len(self.active_connections),
            "max": self.max_connections,
            "available": self.max_connections - len(self.active_connections)
        }


# Создаем глобальный экземпляр хаба
websocket_hub = WebSocketHub() 