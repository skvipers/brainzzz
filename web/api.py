import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из нашего проекта
try:
    from brains.brain import Brain
    from brains.genome import Genome
    from brains.growth_rules import GrowthRules
    from dist.parallel_engine import ParallelEngine
    from tasks.task_manager import TaskManager
    from tasks.xor_task import XORTask
    from tasks.sequence_task import SequenceTask
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Создаем заглушки для тестирования
    Brain = None
    Genome = None
    GrowthRules = None
    ParallelEngine = None
    TaskManager = None
    XORTask = None
    SequenceTask = None

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import List, Dict, Any
import logging
from datetime import datetime

# Redis и Event Bus
from .redis_manager import redis_manager
from .event_bus import event_bus
from .settings import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan менеджер для инициализации
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global parallel_engine, task_manager, population
    
    logger.info("🚀 Запуск инкубатора мозгов...")
    
    # Инициализируем Redis
    try:
        redis_connected = await redis_manager.connect()
        if redis_connected:
            logger.info("✅ Redis подключен успешно")
        else:
            logger.warning("⚠️ Redis недоступен, работаем без него")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {e}")
    
    # Инициализируем Event Bus
    try:
        await event_bus.start()
        logger.info("✅ Event Bus запущен")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска Event Bus: {e}")
    
    # Инициализируем параллельный движок
    try:
        parallel_engine = ParallelEngine()
        logger.info("✅ Параллельный движок инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Ray: {e}")
        parallel_engine = None
    
    # Инициализируем менеджер задач
    task_manager = TaskManager()
    task_manager.add_task(XORTask())
    task_manager.add_task(SequenceTask())
    logger.info("✅ Менеджер задач инициализирован")
    
    # Создаем начальную популяцию
    await create_initial_population(20)
    logger.info("✅ Начальная популяция создана")
    
    yield
    
    # Shutdown
    logger.info("🛑 Завершение работы инкубатора мозгов...")
    
    # Останавливаем Event Bus
    try:
        await event_bus.stop()
        logger.info("🛑 Event Bus остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки Event Bus: {e}")
    
    # Отключаемся от Redis
    try:
        await redis_manager.disconnect()
        logger.info("🔌 Redis отключен")
    except Exception as e:
        logger.error(f"Ошибка отключения от Redis: {e}")

# Создаем FastAPI приложение
app = FastAPI(
    title="🧠 Инкубатор Мозгов",
    description="Эволюционная система для когнитивных структур",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="web"), name="static")

# Глобальные переменные
parallel_engine: ParallelEngine = None
task_manager: TaskManager = None
population: List[Brain] = []
websocket_connections: List[WebSocket] = []

# Модели данных (Pydantic)
from pydantic import BaseModel

class BrainInfo(BaseModel):
    id: int
    nodes: int
    connections: int
    gp: float
    fitness: float
    age: int

class PopulationStats(BaseModel):
    size: int
    avg_fitness: float
    max_fitness: float
    avg_nodes: float
    avg_connections: float
    generation: int

class EvolutionRequest(BaseModel):
    mutation_rate: float = 0.3
    population_size: int = 20

# WebSocket менеджер
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket подключен. Всего: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket отключен. Всего: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if self.active_connections:
            await asyncio.gather(
                *[connection.send_text(message) for connection in self.active_connections]
            )

manager = ConnectionManager()

async def create_initial_population(size: int):
    """Создает начальную популяцию мозгов."""
    global population
    
    population = []
    for i in range(size):
        genome = Genome(input_size=2, output_size=1, hidden_size=3)
        growth_rules = GrowthRules()
        brain = Brain(genome, growth_rules)
        brain.gp = 10.0  # Начальные очки развития
        population.append(brain)
    
    logger.info(f"Создана популяция из {len(population)} мозгов")

# API endpoints
@app.get("/brain_visualizer.html", response_class=HTMLResponse)
async def brain_visualizer():
    """Страница визуализатора мозгов."""
    with open("web/brain_visualizer.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Инкубатор Мозгов</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .stats { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Инкубатор Мозгов</h1>
                <p>Эволюционная система для когнитивных структур</p>
            </div>
            
            <div class="stats">
                <h3>📊 Статистика популяции</h3>
                <p>Размер: <span id="population-size">-</span></p>
                <p>Средняя приспособленность: <span id="avg-fitness">-</span></p>
                <p>Поколение: <span id="generation">-</span></p>
            </div>
            
            <div class="stats" style="margin-top: 20px;">
                <h3>🔴 Статус Redis</h3>
                <p>Статус: <span id="redis-status">-</span></p>
                <p>Версия: <span id="redis-version">-</span></p>
                <p>Клиенты: <span id="redis-clients">-</span></p>
            </div>
            
            <div style="margin-top: 20px;">
                <button class="button" onclick="startEvolution()">🚀 Запустить эволюцию</button>
                <button class="button" onclick="evaluatePopulation()">📊 Оценить популяцию</button>
                <button class="button" onclick="getStats()">📈 Обновить статистику</button>
                <button class="button" onclick="checkRedisStatus()">🔴 Проверить Redis</button>
                <button class="button" onclick="openVisualizer()">🧠 Визуализатор</button>
            </div>
            
            <div id="logs" style="margin-top: 20px; background: #000; color: #0f0; padding: 10px; border-radius: 4px; font-family: monospace; height: 200px; overflow-y: auto;">
                <div>🚀 Система готова к работе...</div>
            </div>
        </div>
        
        <script>
            let ws = null;
            
            function connectWebSocket() {
                ws = new WebSocket('ws://localhost:8000/ws');
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addLog(data.message || JSON.stringify(data));
                };
                ws.onclose = function() {
                    addLog('❌ WebSocket соединение закрыто');
                    setTimeout(connectWebSocket, 1000);
                };
            }
            
            function addLog(message) {
                const logs = document.getElementById('logs');
                const div = document.createElement('div');
                div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                logs.appendChild(div);
                logs.scrollTop = logs.scrollHeight;
            }
            
            async function startEvolution() {
                const response = await fetch('/api/evolve', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mutation_rate: 0.3, population_size: 20})
                });
                const result = await response.json();
                addLog(`🚀 Эволюция запущена: ${result.message}`);
            }
            
            async function evaluatePopulation() {
                const response = await fetch('/api/evaluate');
                const result = await response.json();
                addLog(`📊 Оценка завершена: ${result.message}`);
            }
            
            async function getStats() {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('population-size').textContent = stats.size;
                document.getElementById('avg-fitness').textContent = stats.avg_fitness.toFixed(3);
                document.getElementById('generation').textContent = stats.generation;
                
                addLog(`📈 Статистика обновлена`);
            }
            
            async function checkRedisStatus() {
                try {
                    const response = await fetch('/api/redis/status');
                    const status = await response.json();
                    
                    document.getElementById('redis-status').textContent = status.status;
                    document.getElementById('redis-version').textContent = status.stats.redis_version || '-';
                    document.getElementById('redis-clients').textContent = status.stats.connected_clients || '-';
                    
                    if (status.status === 'connected') {
                        addLog(`✅ Redis подключен: ${status.stats.redis_version}`);
                    } else {
                        addLog(`❌ Redis недоступен: ${status.status}`);
                    }
                } catch (error) {
                    addLog(`❌ Ошибка проверки Redis: ${error.message}`);
                }
            }
            
            function openVisualizer() {
                window.open('/brain_visualizer.html', '_blank', 'width=1400,height=800');
            }
            
            // Подключаемся при загрузке
            connectWebSocket();
            getStats();
            checkRedisStatus();
        </script>
    </body>
    </html>
    """

@app.get("/api/stats", response_model=PopulationStats)
async def get_population_stats():
    """Получает статистику популяции."""
    try:
        if not population:
            # Возвращаем тестовую статистику, если популяция не создана
            return PopulationStats(
                size=0,
                avg_fitness=0.0,
                max_fitness=0.0,
                avg_nodes=0.0,
                avg_connections=0.0,
                generation=0
            )
        
        if parallel_engine:
            stats = parallel_engine.get_population_statistics(population, task_manager)
            return PopulationStats(
                size=len(population),
                avg_fitness=stats['avg_fitness'],
                max_fitness=stats['max_fitness'],
                avg_nodes=stats['avg_nodes'],
                avg_connections=stats.get('avg_complexity', 0.0),  # Используем complexity как connections
                generation=0  # TODO: добавить счетчик поколений
            )
        else:
            # Простая статистика без Ray
            try:
                fitnesses = [brain.fitness for brain in population]
                nodes = [brain.phenotype.num_nodes for brain in population]
                connections = [len(brain.genome.connection_genes) for brain in population]
                
                return PopulationStats(
                    size=len(population),
                    avg_fitness=sum(fitnesses) / len(fitnesses) if fitnesses else 0,
                    max_fitness=max(fitnesses) if fitnesses else 0,
                    avg_nodes=sum(nodes) / len(nodes) if nodes else 0,
                    avg_connections=sum(connections) / len(connections) if connections else 0,
                    generation=0
                )
            except Exception as e:
                logger.error(f"Ошибка простой статистики: {e}")
                return PopulationStats(
                    size=len(population),
                    avg_fitness=0.0,
                    max_fitness=0.0,
                    avg_nodes=0.0,
                    avg_connections=0.0,
                    generation=0
                )
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        # Возвращаем базовую статистику при ошибке
        return PopulationStats(
            size=0,
            avg_fitness=0.0,
            max_fitness=0.0,
            avg_nodes=0.0,
            avg_connections=0.0,
            generation=0
        )

@app.get("/api/redis/status")
async def get_redis_status():
    """Получает статус Redis."""
    try:
        if redis_manager.is_connected:
            stats = await redis_manager.get_system_stats()
            return {
                "status": "connected",
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "disconnected",
                "stats": {},
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Ошибка получения статуса Redis: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/population/{brain_id}")
async def get_brain_detail(brain_id: int):
    """Получает детальную информацию о конкретном мозге."""
    if not population:
        raise HTTPException(status_code=404, detail="Популяция не создана")
    
    if brain_id >= len(population) or brain_id < 0:
        raise HTTPException(status_code=404, detail="Мозг с таким ID не найден")
    
    brain = population[brain_id]
    
    try:
        # Получаем детальную информацию о структуре
        nodes = []
        connections = []
        
        # Информация об узлах
        num_nodes = brain.phenotype.num_nodes
        for i in range(num_nodes):
            node_info = {
                "id": i,
                "type": "hidden",  # По умолчанию
                "activation": "sigmoid",  # По умолчанию sigmoid
                "bias": brain.genome.node_genes[i].bias if i < len(brain.genome.node_genes) else 0.0,
                "threshold": brain.genome.node_genes[i].threshold if i < len(brain.genome.node_genes) else 0.0
            }
            
            # Определяем тип узла
            if i < brain.genome.input_size:
                node_info["type"] = "input"
            elif i >= brain.genome.input_size + brain.genome.hidden_size:
                node_info["type"] = "output"
            elif hasattr(brain.genome.node_genes[i], 'memory') and brain.genome.node_genes[i].memory:
                node_info["type"] = "memory"
            
            nodes.append(node_info)
        
        # Информация о связях
        for i, conn in enumerate(brain.genome.connection_genes):
            connection_info = {
                "id": i,
                "from": conn.from_node,
                "to": conn.to_node,
                "weight": conn.weight,
                "plasticity": conn.plasticity,
                "enabled": conn.enabled
            }
            connections.append(connection_info)
        
        brain_detail = {
            "id": brain_id,
            "nodes": nodes,
            "connections": connections,
            "gp": brain.gp,
            "fitness": brain.fitness,
            "age": brain.age,
            "genome_size": len(brain.genome.node_genes),
            "connection_count": len(brain.genome.connection_genes)
        }
        
        return brain_detail
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей мозга {brain_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения деталей: {str(e)}")

@app.get("/api/population", response_model=List[BrainInfo])
async def get_population():
    """Получает информацию о популяции."""
    if not population:
        raise HTTPException(status_code=404, detail="Популяция не создана")
    
    brain_infos = []
    for i, brain in enumerate(population):
        brain_infos.append(BrainInfo(
            id=i,
            nodes=brain.phenotype.num_nodes,
            connections=len(brain.genome.connection_genes),
            gp=brain.gp,
            fitness=brain.fitness,
            age=brain.age
        ))
    
    return brain_infos

@app.post("/api/evaluate")
async def evaluate_population():
    """Оценивает всю популяцию."""
    if not population:
        raise HTTPException(status_code=404, detail="Популяция не создана")
    
    if not task_manager:
        raise HTTPException(status_code=500, detail="Менеджер задач не инициализирован")
    
    try:
        if parallel_engine:
            # Параллельная оценка
            results = parallel_engine.evaluate_population_parallel(population, task_manager)
            message = f"Параллельная оценка завершена: {len(results)} мозгов"
        else:
            # Последовательная оценка
            for brain in population:
                brain.evaluate_fitness(task_manager)
            message = f"Последовательная оценка завершена: {len(population)} мозгов"
        
        # Отправляем обновление через WebSocket
        await manager.broadcast(json.dumps({
            "type": "evaluation_complete",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }))
        
        return {"message": message, "success": True}
        
    except Exception as e:
        logger.error(f"Ошибка оценки популяции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка оценки: {str(e)}")

@app.post("/api/evolve")
async def evolve_population(request: EvolutionRequest):
    """Запускает эволюцию популяции."""
    global population
    
    if not population:
        raise HTTPException(status_code=404, detail="Популяция не создана")
    
    try:
        # Проверяем, нужно ли изменить размер популяции
        current_size = len(population)
        target_size = request.population_size
        
        if target_size != current_size:
            logger.info(f"Изменение размера популяции с {current_size} на {target_size}")
            
            if target_size > current_size:
                # Увеличиваем популяцию - добавляем новые мозги
                for i in range(target_size - current_size):
                    genome = Genome(input_size=2, output_size=1, hidden_size=3)
                    growth_rules = GrowthRules()
                    brain = Brain(genome, growth_rules)
                    brain.gp = 10.0  # Начальные очки развития
                    population.append(brain)
                message = f"Популяция увеличена с {current_size} до {target_size} мозгов"
            else:
                # Уменьшаем популяцию - оставляем лучших
                # Сортируем по fitness и оставляем лучших
                population.sort(key=lambda x: x.fitness, reverse=True)
                population = population[:target_size]
                message = f"Популяция уменьшена с {current_size} до {target_size} мозгов (оставлены лучшие)"
        
        # Применяем эволюцию (мутации)
        if parallel_engine:
            # Параллельная эволюция
            evolved_population = parallel_engine.evolve_population_parallel(
                population, request.mutation_rate
            )
            evolution_message = f"Параллельная эволюция завершена: {len(evolved_population)} мозгов"
        else:
            # Последовательная эволюция
            evolved_population = []
            for brain in population:
                brain_copy = brain.clone()
                if brain_copy.mutate(request.mutation_rate):
                    evolved_population.append(brain_copy)
                else:
                    evolved_population.append(brain)
            evolution_message = f"Последовательная эволюция завершена: {len(evolved_population)} мозгов"
        
        # Обновляем популяцию
        population = evolved_population
        
        # Отправляем обновление через WebSocket
        await manager.broadcast(json.dumps({
            "type": "evolution_complete",
            "message": f"{message}. {evolution_message}",
            "population_size": len(population),
            "timestamp": datetime.now().isoformat()
        }))
        
        return {
            "message": f"{message}. {evolution_message}",
            "population_size": len(population),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Ошибка эволюции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка эволюции: {str(e)}")

@app.post("/api/population/resize")
async def resize_population(request: EvolutionRequest):
    """Изменяет размер популяции без эволюции."""
    global population
    
    if not population:
        raise HTTPException(status_code=404, detail="Популяция не создана")
    
    try:
        current_size = len(population)
        target_size = request.population_size
        
        if target_size == current_size:
            return {
                "message": f"Размер популяции уже {current_size}",
                "population_size": current_size,
                "success": True
            }
        
        if target_size > current_size:
            # Увеличиваем популяцию
            for i in range(target_size - current_size):
                genome = Genome(input_size=2, output_size=1, hidden_size=3)
                growth_rules = GrowthRules()
                brain = Brain(genome, growth_rules)
                brain.gp = 10.0  # Начальные очки развития
                population.append(brain)
            message = f"Популяция увеличена с {current_size} до {target_size} мозгов"
        else:
            # Уменьшаем популяцию - оставляем лучших
            population.sort(key=lambda x: x.fitness, reverse=True)
            population = population[:target_size]
            message = f"Популяция уменьшена с {current_size} до {target_size} мозгов (оставлены лучшие)"
        
        # Отправляем обновление через WebSocket
        await manager.broadcast(json.dumps({
            "type": "population_resized",
            "message": message,
            "population_size": len(population),
            "timestamp": datetime.now().isoformat()
        }))
        
        return {
            "message": message,
            "population_size": len(population),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Ошибка изменения размера популяции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка изменения размера: {str(e)}")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Ждем сообщения от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обрабатываем команды от клиента
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.api:app", host="0.0.0.0", port=8000, reload=True) 