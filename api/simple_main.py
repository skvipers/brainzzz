"""
Упрощенная версия FastAPI приложения для тестирования.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="🧠 Brainzzz API (Simple)",
    description="Упрощенная версия API для тестирования",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Простые тестовые endpoints


@app.get("/")
async def root():
    """Главная страница API."""
    return {
        "message": "🧠 Brainzzz API (Simple)",
        "version": "1.0.0",
        "status": "working",
    }


@app.get("/api/health")
async def health_check():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0",
    }


@app.get("/api/population")
async def get_population(limit: int = 10):
    """Получение популяции (mock данные)."""
    logger.info(f"Запрос популяции с лимитом: {limit}")
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


@app.get("/api/stats")
async def get_stats():
    """Получение статистики (mock данные)."""
    logger.info("Запрос статистики популяции")
    return {
        "size": 20,
        "avg_fitness": 0.390,
        "max_fitness": 0.454,
        "avg_nodes": 8.0,
        "avg_connections": 10.0,
        "generation": 1,
    }


@app.post("/api/evolve")
async def start_evolution(data: dict):
    """Запуск эволюции (mock)."""
    logger.info(f"Запрос запуска эволюции: {data}")
    return {
        "message": "Эволюция запущена (mock)",
        "status": "success",
        "mutation_rate": data.get("mutation_rate", 0.3),
        "population_size": data.get("population_size", 20),
    }


@app.get("/api/population/{brain_id}")
async def get_brain(brain_id: int):
    """Получение данных конкретного мозга."""
    logger.info(f"Запрос данных для мозга #{brain_id}")

    # Валидируем brain_id
    if brain_id <= 0 or brain_id > 20:
        return {"error": "ID мозга должен быть от 1 до 20"}

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
        f"{len(mock_brain['nodes'])} узлов, {len(mock_brain['connections'])} связей"
    )
    return mock_brain


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
