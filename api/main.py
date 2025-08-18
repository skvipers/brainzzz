"""
Основной FastAPI приложение для Brainzzz API.
"""

import asyncio
import logging
from typing import Optional

from core.adapters import redis_adapter
from core.settings import settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ws.hub import WebSocketHub

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="🧠 Brainzzz API",
    description="API для управления симуляцией эволюции нейронных сетей",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket хаб
websocket_hub = WebSocketHub()


# Startup и shutdown события
@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения."""
    logger.info("🚀 Brainzzz API запускается...")
    logger.info(f"WebSocket лимит соединений: {websocket_hub.max_connections}")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения."""
    logger.info("🛑 Brainzzz API останавливается...")
    await websocket_hub.stop_redis_listener()
    # Принудительно закрываем все WebSocket соединения
    for websocket in list(websocket_hub.active_connections):
        try:
            await websocket.close(code=1001, reason="Server shutdown")
        except Exception:
            pass
    websocket_hub.active_connections.clear()
    logger.info("WebSocket соединения закрыты")


# Глобальная переменная для размера популяции
POPULATION_SIZE = 20

# Простые тестовые endpoints


@app.get("/")
async def root():
    """Главная страница API."""
    return {"message": "🧠 Brainzzz API", "version": "1.0.0", "status": "working"}


@app.get("/api/health")
async def health_check():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0",
    }


@app.get("/api/population")
async def get_population(limit: Optional[int] = None):
    """Получение популяции (mock данные)."""
    # Если limit не указан, используем глобальный размер популяции
    if limit is None:
        limit = POPULATION_SIZE

    logger.info(f"Запрос популяции с лимитом: {limit}")
    mock_population = []

    # Генерируем мозги от 1 до POPULATION_SIZE
    for i in range(1, POPULATION_SIZE + 1):
        mock_population.append(
            {
                "id": i,
                "nodes": 7 + (i % 5),  # 7-11 узлов
                "connections": 8 + (i % 7),  # 8-14 связей
                "gp": 3.5 + (i * 0.1),  # GP от 3.6 до 5.5
                "fitness": 0.3 + (i * 0.01),  # Fitness от 0.31 до 0.5
                "age": 1 + (i % 3),  # Age от 1 до 3
            }
        )

    logger.info(f"Возвращено {len(mock_population)} мозгов")
    return mock_population


@app.get("/api/stats")
async def get_stats():
    """Получение статистики (mock данных)."""
    logger.info("Запрос статистики популяции")
    return {
        "size": POPULATION_SIZE,
        "avg_fitness": 0.390,
        "max_fitness": 0.454,
        "avg_nodes": 8.0,
        "avg_connections": 10.0,
        "generation": 1,
    }


@app.get("/api/ws/stats")
async def get_websocket_stats():
    """Получение статистики WebSocket соединений."""
    return websocket_hub.get_connection_stats()


@app.get("/api/ws/status")
async def get_websocket_status():
    """Проверка статуса WebSocket сервера."""
    return {
        "status": "available",
        "max_connections": websocket_hub.max_connections,
        "active_connections": len(websocket_hub.active_connections),
        "available_connections": websocket_hub.max_connections
        - len(websocket_hub.active_connections),
        "can_accept": len(websocket_hub.active_connections)
        < websocket_hub.max_connections,
    }


@app.get("/api/ws/test")
async def test_websocket_connection():
    """Тестирование WebSocket соединения."""
    import websockets

    try:
        # Пытаемся подключиться к WebSocket серверу
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            # Отправляем тестовое сообщение
            await websocket.send("test")
            # Получаем ответ
            response = await websocket.recv()
            await websocket.close()

            return {
                "status": "success",
                "message": "WebSocket соединение работает",
                "response": response,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"WebSocket ошибка: {str(e)}",
            "error_type": type(e).__name__,
        }


@app.post("/api/ws/cleanup")
async def cleanup_websocket_connections():
    """Очистка мертвых WebSocket соединений."""
    await websocket_hub.cleanup_dead_connections()
    return {
        "status": "success",
        "message": "Очистка завершена",
        "stats": websocket_hub.get_connection_stats(),
    }


@app.post("/api/ws/reset")
async def reset_all_websocket_connections():
    """Принудительный сброс всех WebSocket соединений."""
    logger.warning("🔄 Принудительный сброс всех WebSocket соединений")

    # Закрываем все активные соединения
    connections_to_close = list(websocket_hub.active_connections)
    for websocket in connections_to_close:
        try:
            await websocket.close(code=1001, reason="Server reset")
        except Exception as e:
            logger.error(f"Ошибка закрытия WebSocket: {e}")

    # Очищаем список соединений
    websocket_hub.active_connections.clear()

    logger.info(f"✅ Сброшено {len(connections_to_close)} WebSocket соединений")
    return {
        "status": "success",
        "message": f"Сброшено {len(connections_to_close)} соединений",
        "stats": websocket_hub.get_connection_stats(),
    }


@app.post("/api/evolve")
async def start_evolution(data: dict):
    """Запуск эволюции (mock)."""
    global POPULATION_SIZE

    # Обновляем размер популяции
    new_size = data.get("population_size", 20)
    POPULATION_SIZE = new_size

    logger.info(f"Запрос запуска эволюции: {data}")
    logger.info(f"Размер популяции изменен на: {POPULATION_SIZE}")

    return {
        "message": "Эволюция запущена (mock)",
        "status": "success",
        "mutation_rate": data.get("mutation_rate", 0.3),
        "population_size": POPULATION_SIZE,
    }


@app.get("/api/population/{brain_id}")
async def get_brain(brain_id: int):
    """Получение данных конкретного мозга."""
    logger.info(f"Запрос данных для мозга #{brain_id}")

    # Валидируем brain_id
    if brain_id <= 0 or brain_id > POPULATION_SIZE:
        return {"error": f"ID мозга должен быть от 1 до {POPULATION_SIZE}"}

    # Генерируем количество узлов и связей, соответствующее сводным данным
    node_count = 7 + (brain_id % 5)  # 7-11 узлов (как в сводных данных)
    connection_count = 8 + (brain_id % 7)  # 8-14 связей (как в сводных данных)

    # Создаем узлы
    nodes = []
    for i in range(1, node_count + 1):
        if i == 1:
            node_type = "input"
        elif i == node_count:
            node_type = "output"
        else:
            node_type = "hidden"

        nodes.append(
            {
                "id": i,
                "type": node_type,
                "activation": "sigmoid",
                "bias": round(0.1 + (i * 0.05), 2),
                "threshold": round(0.3 + (i * 0.1), 2),
            }
        )

    # Создаем связи (соединяем узлы последовательно)
    connections = []
    for i in range(1, connection_count + 1):
        if i < node_count:  # Связь между существующими узлами
            connections.append(
                {
                    "id": i,
                    "from": i,
                    "to": i + 1,
                    "weight": round(-0.8 + (i * 0.3), 2),
                    "plasticity": 0.1,
                    "enabled": True,
                }
            )
        else:  # Дополнительные связи между случайными узлами
            from_node = (i % node_count) + 1
            to_node = ((i + 1) % node_count) + 1
            if from_node != to_node:
                # Некоторые мозги имеют неактивные связи для тестирования
                # Мозги 3, 7, 11, 15, 19 имеют неактивные связи
                is_disabled = (
                    brain_id in [3, 7, 11, 15, 19] and i > connection_count - 2
                )
                connections.append(
                    {
                        "id": i,
                        "from": from_node,
                        "to": to_node,
                        "weight": round(-0.5 + (i * 0.2), 2),
                        "plasticity": 0.1,
                        "enabled": not is_disabled,
                    }
                )

    mock_brain = {
        "id": brain_id,
        "nodes": nodes,
        "connections": connections,
        "gp": 3.5 + (brain_id * 0.1),  # GP от 3.6 до 5.5
        "fitness": 0.3 + (brain_id * 0.01),  # Fitness от 0.31 до 0.5
        "age": 1 + (brain_id % 3),  # Age от 1 до 3
    }

    logger.info(
        f"Успешно возвращены данные для мозга #{brain_id}: "
        f"{len(nodes)} узлов, {len(connections)} связей"
    )
    return mock_brain


@app.post("/api/test-redis")
async def test_redis_event():
    """Тестовый endpoint для публикации события в Redis."""
    try:
        # Подключаемся к Redis
        await redis_adapter.connect()

        # Публикуем тестовое событие
        success = await redis_adapter.publish_event(
            "test_event",
            {
                "message": "Тестовое событие из API",
                "timestamp": "2025-01-18T00:00:00Z",
                "data": {"test": True, "value": 42},
            },
        )

        if success:
            return {
                "status": "success",
                "message": "Событие опубликовано в Redis",
                "channel": "brainzzz.events",
            }
        else:
            return {"status": "error", "message": "Не удалось опубликовать событие"}

    except Exception as e:
        logger.error(f"Ошибка тестирования Redis: {e}")
        return {"status": "error", "message": f"Ошибка: {str(e)}"}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time обновлений."""
    client_id = id(websocket)
    logger.info(f"🔌 Попытка подключения WebSocket #{client_id}")

    try:
        # Проверяем лимит соединений перед подключением
        if len(websocket_hub.active_connections) >= websocket_hub.max_connections:
            logger.warning(
                f"❌ Достигнут лимит WebSocket соединений: "
                f"{websocket_hub.max_connections}"
            )
            await websocket.close(code=1013, reason="Too many connections")
            return

        await websocket_hub.connect(websocket)
        logger.info(f"✅ WebSocket #{client_id} успешно подключен")

        # Проверяем, что соединение действительно установлено
        if websocket not in websocket_hub.active_connections:
            logger.warning(
                f"⚠️ WebSocket #{client_id} не добавлен в активные соединения"
            )
            return

        # Отправляем ping каждые 30 секунд для проверки соединения
        ping_task = asyncio.create_task(ping_websocket(websocket, client_id))

        try:
            while True:
                # Держим соединение открытым
                data = await websocket.receive_text()
                logger.debug(f"📨 Получено сообщение от WebSocket #{client_id}: {data}")

        except WebSocketDisconnect:
            logger.info(f"🔌 WebSocket #{client_id} клиент отключился")
        except Exception as e:
            logger.error(f"❌ Ошибка WebSocket #{client_id}: {e}")
        finally:
            # Отменяем ping задачу
            ping_task.cancel()
            websocket_hub.disconnect(websocket)
            logger.info(f"🧹 WebSocket #{client_id} очищен")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка WebSocket #{client_id}: {e}")
        websocket_hub.disconnect(websocket)
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass


async def ping_websocket(websocket: WebSocket, client_id: int):
    """Отправка ping сообщений для проверки соединения."""
    try:
        while True:
            await asyncio.sleep(30)  # Ping каждые 30 секунд
            if websocket in websocket_hub.active_connections:
                try:
                    await websocket.send_text('{"type": "ping"}')
                    logger.debug(f"🏓 Ping отправлен WebSocket #{client_id}")
                except Exception as e:
                    logger.warning(
                        f"⚠️ Не удалось отправить ping WebSocket #{client_id}: {e}"
                    )
                    break
            else:
                break
    except asyncio.CancelledError:
        logger.debug(f"🏓 Ping задача отменена для WebSocket #{client_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка ping WebSocket #{client_id}: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
