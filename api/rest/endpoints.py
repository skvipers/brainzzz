"""
REST API endpoints для управления симуляцией.
"""

import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pathlib import Path

from api.core.schemas import PopulationStats, BrainStats
from api.core.adapters import duckdb_adapter, redis_adapter
from api.core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0"
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
            "connections": {
                "redis": redis_status,
                "duckdb": duckdb_status
            },
            "timestamp": "2025-01-18T00:00:00Z"
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
            return {
                "message": "DuckDB недоступен",
                "data": []
            }
        
        snapshots = duckdb_adapter.get_population_snapshots(limit)
        return {
            "data": snapshots,
            "count": len(snapshots)
        }
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
        for i in range(1, min(limit + 1, 21)):  # Максимум 20 мозгов для тестирования
            mock_population.append({
                "id": i,
                "nodes": 7 + (i % 5),  # 7-11 узлов
                "connections": 8 + (i % 7),  # 8-14 связей
                "gp": 3.5 + (i * 0.1),  # GP от 3.6 до 5.5
                "fitness": 0.3 + (i * 0.01),  # Fitness от 0.31 до 0.5
                "age": 1 + (i % 3)  # Age от 1 до 3
            })
        
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
        if brain_id <= 0:
            raise HTTPException(status_code=400, detail="ID мозга должен быть положительным числом")
        
        # Возвращаем mock данные для тестирования фронтенда
        mock_brain = {
            "id": brain_id,
            "nodes": [
                {
                    "id": 1,
                    "type": "input",
                    "activation": "sigmoid",
                    "bias": 0.1,
                    "threshold": 0.5
                },
                {
                    "id": 2,
                    "type": "hidden",
                    "activation": "sigmoid",
                    "bias": -0.2,
                    "threshold": 0.3
                },
                {
                    "id": 3,
                    "type": "output",
                    "activation": "sigmoid",
                    "bias": 0.0,
                    "threshold": 0.7
                }
            ],
            "connections": [
                {
                    "id": 1,
                    "from": 1,
                    "to": 2,
                    "weight": 0.8,
                    "plasticity": 0.1,
                    "enabled": True
                },
                {
                    "id": 2,
                    "from": 2,
                    "to": 3,
                    "weight": -0.5,
                    "plasticity": 0.1,
                    "enabled": True
                }
            ],
            "gp": 4.03,
            "fitness": 0.403,
            "age": 1
        }
        
        logger.info(f"Успешно возвращены данные для мозга #{brain_id}: {len(mock_brain['nodes'])} узлов, {len(mock_brain['connections'])} связей")
        return mock_brain
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения мозга {brain_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения мозга: {str(e)}")


@router.get("/stats")
async def get_stats():
    """Получение общей статистики (обратная совместимость)."""
    try:
        logger.info("Запрос статистики популяции")
        
        # Возвращаем mock статистику для тестирования фронтенда
        # Пока возвращаем базовую статистику, позже можно сделать динамической
        return {
            "size": 20,  # Увеличиваем размер популяции
            "avg_fitness": 0.390,
            "max_fitness": 0.454,
            "avg_nodes": 8.0,
            "avg_connections": 10.0,
            "generation": 50
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.get("/brains/{brain_id}/stats")
async def get_brain_stats(brain_id: str, limit: int = 100):
    """Получение статистики конкретного мозга."""
    try:
        if not duckdb_adapter.connected:
            return {
                "message": "DuckDB недоступен",
                "data": []
            }
        
        snapshots = duckdb_adapter.get_brain_snapshots(brain_id, limit)
        return {
            "brain_id": brain_id,
            "data": snapshots,
            "count": len(snapshots)
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики мозга: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.post("/control/pause")
async def pause_simulation():
    """Приостановка симуляции."""
    try:
        # Отправляем команду через Redis
        success = await redis_adapter.publish_event("control", {
            "action": "pause",
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            return {"message": "Команда паузы отправлена", "status": "success"}
        else:
            return {"message": "Redis недоступен", "status": "warning"}
            
    except Exception as e:
        logger.error(f"Ошибка отправки команды паузы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отправки команды")


@router.post("/control/resume")
async def resume_simulation():
    """Возобновление симуляции."""
    try:
        success = await redis_adapter.publish_event("control", {
            "action": "resume",
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            return {"message": "Команда возобновления отправлена", "status": "success"}
        else:
            return {"message": "Redis недоступен", "status": "warning"}
            
    except Exception as e:
        logger.error(f"Ошибка отправки команды возобновления: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отправки команды")


@router.post("/control/snapshot")
async def create_snapshot():
    """Создание снапшота."""
    try:
        success = await redis_adapter.publish_event("control", {
            "action": "snapshot",
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            return {"message": "Команда создания снапшота отправлена", "status": "success"}
        else:
            return {"message": "Redis недоступен", "status": "warning"}
            
    except Exception as e:
        logger.error(f"Ошибка отправки команды снапшота: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отправки команды")


@router.get("/snapshots")
async def list_snapshots():
    """Список доступных снапшотов."""
    try:
        snapshots_dir = settings.DATA_DIR / "snapshots"
        if not snapshots_dir.exists():
            return {"data": [], "count": 0}
        
        snapshots = []
        for snapshot_file in snapshots_dir.glob("*.json"):
            try:
                with open(snapshot_file, 'r') as f:
                    snapshot_data = json.load(f)
                    snapshots.append({
                        "filename": snapshot_file.name,
                        "size": snapshot_file.stat().st_size,
                        "modified": snapshot_file.stat().st_mtime,
                        "data": snapshot_data
                    })
            except Exception as e:
                logger.warning(f"Ошибка чтения снапшота {snapshot_file}: {e}")
        
        return {
            "data": snapshots,
            "count": len(snapshots)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка снапшотов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения снапшотов")


@router.post("/evolve")
async def start_evolution(data: dict):
    """Запуск эволюции."""
    try:
        logger.info(f"Запрос запуска эволюции с параметрами: {data}")
        
        # Валидируем входные данные
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Данные должны быть объектом")
        
        mutation_rate = data.get("mutation_rate", 0.3)
        population_size = data.get("population_size", 20)
        
        # Проверяем диапазоны значений
        if not (0.0 <= mutation_rate <= 1.0):
            raise HTTPException(status_code=400, detail="mutation_rate должен быть от 0.0 до 1.0")
        
        if not (1 <= population_size <= 1000):
            raise HTTPException(status_code=400, detail="population_size должен быть от 1 до 1000")
        
        # Отправляем команду через Redis
        success = await redis_adapter.publish_event("evolution", {
            "action": "start",
            "mutation_rate": mutation_rate,
            "population_size": population_size,
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            logger.info(f"Эволюция запущена успешно: mutation_rate={mutation_rate}, population_size={population_size}")
            return {
                "message": "Эволюция запущена",
                "status": "success",
                "mutation_rate": mutation_rate,
                "population_size": population_size
            }
        else:
            logger.warning("Redis недоступен для запуска эволюции")
            return {"message": "Redis недоступен", "status": "warning"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка запуска эволюции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка запуска эволюции: {str(e)}")


@router.post("/evaluate")
async def evaluate_population():
    """Оценка популяции."""
    try:
        # Отправляем команду через Redis
        success = await redis_adapter.publish_event("evaluation", {
            "action": "start",
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            return {"message": "Оценка популяции запущена", "status": "success"}
        else:
            return {"message": "Redis недоступен", "status": "warning"}
            
    except Exception as e:
        logger.error(f"Ошибка оценки популяции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка оценки популяции")


@router.post("/population/resize")
async def resize_population(data: dict):
    """Изменение размера популяции."""
    try:
        logger.info(f"Запрос изменения размера популяции с параметрами: {data}")
        
        # Валидируем входные данные
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Данные должны быть объектом")
        
        population_size = data.get("population_size", 20)
        mutation_rate = data.get("mutation_rate", 0.3)
        
        # Проверяем диапазоны значений
        if not (1 <= population_size <= 1000):
            raise HTTPException(status_code=400, detail="population_size должен быть от 1 до 1000")
        
        if not (0.0 <= mutation_rate <= 1.0):
            raise HTTPException(status_code=400, detail="mutation_rate должен быть от 0.0 до 1.0")
        
        # Отправляем команду через Redis
        success = await redis_adapter.publish_event("population", {
            "action": "resize",
            "population_size": population_size,
            "mutation_rate": mutation_rate,
            "timestamp": "2025-01-18T00:00:00Z"
        })
        
        if success:
            logger.info(f"Размер популяции изменен успешно: population_size={population_size}, mutation_rate={mutation_rate}")
            return {
                "message": "Размер популяции изменен",
                "status": "success",
                "population_size": population_size,
                "mutation_rate": mutation_rate
            }
        else:
            logger.warning("Redis недоступен для изменения размера популяции")
            return {"message": "Redis недоступен", "status": "warning"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка изменения размера популяции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка изменения размера популяции: {str(e)}") 