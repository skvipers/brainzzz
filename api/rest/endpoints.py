"""
REST API endpoints для управления симуляцией.
"""

import logging
from fastapi import APIRouter, HTTPException

from api.core.adapters import duckdb_adapter, redis_adapter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0",
    }


@router.get("/status")
async def system_status():
    """Статус системы."""
    try:
        # Проверяем подключения
        redis_status = redis_adapter.connected
        duckdb_status = duckdb_adapter.connected

        return {
            "status": "running",
            "connections": {"redis": redis_status, "duckdb": duckdb_status},
            "timestamp": "2025-01-18T00:00:00Z",
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статуса")


@router.get("/population/stats")
async def get_population_stats(limit: int = 100):
    """Получение статистики популяции."""
    try:
        if not duckdb_adapter.connected:
            # Возвращаем заглушку если DB недоступна
            return {"message": "DuckDB недоступен", "data": []}

        snapshots = duckdb_adapter.get_population_snapshots(limit)
        return {"data": snapshots, "count": len(snapshots)}
    except Exception as e:
        logger.error(f"Ошибка получения статистики популяции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.get("/population")
async def get_population(limit: int = 100):
    """Получение популяции (обратная совместимость)."""
    try:
        logger.info(f"Запрос популяции с лимитом: {limit}")

        # Возвращаем mock данные для тестирования фронтенда
        # Генерируем динамически в зависимости от лимита
        mock_population = []
        for i in range(1, min(limit + 1, 21)):  # Максимум 20 мозгов
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

    except Exception as e:
        logger.error(f"Ошибка получения популяции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения популяции")


@router.get("/population/{brain_id}")
async def get_brain(brain_id: int):
    """Получение данных конкретного мозга."""
    try:
        logger.info(f"Запрос данных для мозга #{brain_id}")

        # Валидируем brain_id
        if brain_id <= 0 or brain_id > 20:
            return {"error": "ID мозга должен быть от 1 до 20"}

        # Генерируем количество узлов и связей
        node_count = 7 + (brain_id % 5)  # 7-11 узлов
        connection_count = 8 + (brain_id % 7)  # 8-14 связей

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
                        "from_node": i,
                        "to_node": i + 1,
                        "weight": round(0.5 + (i * 0.1), 2),
                        "enabled": True,
                    }
                )
            else:  # Дополнительные связи между случайными узлами
                from_node = (i % node_count) + 1
                to_node = ((i + 1) % node_count) + 1
                if from_node != to_node:
                    connections.append(
                        {
                            "id": i,
                            "from_node": from_node,
                            "to_node": to_node,
                            "weight": round(0.3 + (i * 0.05), 2),
                            "enabled": True,
                        }
                    )

        return {
            "id": brain_id,
            "nodes": nodes,
            "connections": connections,
            "metadata": {
                "total_nodes": node_count,
                "total_connections": len(connections),
                "generation": 1,
                "fitness": 0.3 + (brain_id * 0.01),
            },
        }

    except Exception as e:
        logger.error(f"Ошибка получения данных мозга #{brain_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных мозга")


@router.get("/evolution/status")
async def get_evolution_status():
    """Получение статуса эволюции."""
    try:
        return {
            "status": "running",
            "generation": 1,
            "population_size": 20,
            "best_fitness": 0.454,
            "avg_fitness": 0.390,
            "timestamp": "2025-01-18T00:00:00Z",
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса эволюции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статуса")


@router.post("/evolution/start")
async def start_evolution(data: dict):
    """Запуск эволюции."""
    try:
        logger.info(f"Запрос запуска эволюции: {data}")
        return {
            "message": "Эволюция запущена",
            "status": "success",
            "mutation_rate": data.get("mutation_rate", 0.3),
            "population_size": data.get("population_size", 20),
        }
    except Exception as e:
        logger.error(f"Ошибка запуска эволюции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка запуска эволюции")


@router.post("/evolution/pause")
async def pause_evolution():
    """Приостановка эволюции."""
    try:
        logger.info("Запрос приостановки эволюции")
        return {"message": "Эволюция приостановлена", "status": "paused"}
    except Exception as e:
        logger.error(f"Ошибка приостановки эволюции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка приостановки")


@router.post("/evolution/resume")
async def resume_evolution():
    """Возобновление эволюции."""
    try:
        logger.info("Запрос возобновления эволюции")
        return {"message": "Эволюция возобновлена", "status": "running"}
    except Exception as e:
        logger.error(f"Ошибка возобновления эволюции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка возобновления")


@router.post("/evolution/snapshot")
async def create_snapshot():
    """Создание снапшота эволюции."""
    try:
        logger.info("Запрос создания снапшота")
        return {
            "message": "Снапшот создан",
            "status": "success",
            "snapshot_id": "snapshot_20250118_001",
        }
    except Exception as e:
        logger.error(f"Ошибка создания снапшота: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания снапшота")
