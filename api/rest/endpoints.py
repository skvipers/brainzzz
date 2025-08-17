"""
REST API endpoints для управления симуляцией.
"""

import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pathlib import Path

from core.schemas import PopulationStats, BrainStats
from core.adapters import duckdb_adapter, redis_adapter
from core.settings import settings

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
        # Возвращаем mock данные для тестирования фронтенда
        mock_population = [
            {
                "id": 1,
                "nodes": 9,
                "connections": 12,
                "gp": 4.03,
                "fitness": 0.403,
                "age": 1
            },
            {
                "id": 2,
                "nodes": 8,
                "connections": 10,
                "gp": 4.54,
                "fitness": 0.454,
                "age": 1
            },
            {
                "id": 3,
                "nodes": 7,
                "connections": 8,
                "gp": 3.85,
                "fitness": 0.313,
                "age": 1
            }
        ]
        
        return mock_population[:limit]
        
    except Exception as e:
        logger.error(f"Ошибка получения популяции: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения популяции")


@router.get("/stats")
async def get_stats():
    """Получение общей статистики (обратная совместимость)."""
    try:
        # Возвращаем mock статистику для тестирования фронтенда
        return {
            "size": 3,
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