from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import List
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="🧠 Инкубатор Мозгов (Тест)",
    description="Простая тестовая версия",
    version="1.0.0"
)

# CORS middleware для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Простые модели данных
from pydantic import BaseModel

class PopulationStats(BaseModel):
    size: int
    avg_fitness: float
    max_fitness: float
    generation: int

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

# Простые API endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Инкубатор Мозгов (Тест)</title>
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
                <h1>🧠 Инкубатор Мозгов (Тест)</h1>
                <p>Простая тестовая версия</p>
            </div>
            
            <div class="stats">
                <h3>📊 Статистика популяции</h3>
                <p>Размер: <span id="population-size">-</span></p>
                <p>Средняя приспособленность: <span id="avg-fitness">-</span></p>
                <p>Поколение: <span id="generation">-</span></p>
            </div>
            
            <div style="margin-top: 20px;">
                <button class="button" onclick="testAPI()">🧪 Тест API</button>
                <button class="button" onclick="getStats()">📈 Обновить статистику</button>
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
            
            async function testAPI() {
                try {
                    const response = await fetch('/api/test');
                    const result = await response.json();
                    addLog(`✅ API тест: ${result.message}`);
                } catch (error) {
                    addLog(`❌ Ошибка API: ${error.message}`);
                }
            }
            
            async function getStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    
                    document.getElementById('population-size').textContent = stats.size;
                    document.getElementById('avg-fitness').textContent = stats.avg_fitness.toFixed(3);
                    document.getElementById('generation').textContent = stats.generation;
                    
                    addLog(`📈 Статистика обновлена`);
                } catch (error) {
                    addLog(`❌ Ошибка получения статистики: ${error.message}`);
                }
            }
            
            // Подключаемся при загрузке
            connectWebSocket();
            getStats();
        </script>
    </body>
    </html>
    """

@app.get("/api/test")
async def test_api():
    """Простой тест API."""
    return {"message": "API работает!", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats", response_model=PopulationStats)
async def get_population_stats():
    """Получает тестовую статистику популяции."""
    return PopulationStats(
        size=20,
        avg_fitness=0.5,
        max_fitness=0.8,
        generation=1
    )

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
    uvicorn.run("web.simple_api:app", host="0.0.0.0", port=8000, reload=True) 