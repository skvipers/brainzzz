"""
Основной FastAPI приложение для Brainzzz API.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.core.settings import settings
from api.core.adapters import redis_adapter, duckdb_adapter
from api.ws.hub import websocket_hub
from api.rest.endpoints import router as rest_router

# Настройка логирования
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan менеджер для инициализации и очистки."""
    
    # Startup
    logger.info("🚀 Запуск Brainzzz API...")
    
    # Инициализируем Redis
    try:
        redis_connected = await redis_adapter.connect()
        if redis_connected:
            logger.info("✅ Redis подключен успешно")
        else:
            logger.warning("⚠️ Redis недоступен, работаем без него")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {e}")
    
    # Инициализируем DuckDB
    try:
        duckdb_connected = duckdb_adapter.connect()
        if duckdb_connected:
            logger.info("✅ DuckDB подключен успешно")
        else:
            logger.warning("⚠️ DuckDB недоступен, работаем без него")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к DuckDB: {e}")
    
    # Запускаем WebSocket Redis listener
    try:
        await websocket_hub.start_redis_listener()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска WebSocket Redis listener: {e}")
    
    logger.info("✅ Brainzzz API запущен")
    
    yield
    
    # Shutdown
    logger.info("🛑 Остановка Brainzzz API...")
    
    try:
        await websocket_hub.stop_redis_listener()
        await redis_adapter.disconnect()
        logger.info("✅ Очистка завершена")
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке: {e}")


# Создаем FastAPI приложение
app = FastAPI(
    title="🧠 Brainzzz API",
    description="API для управления симуляцией эволюции нейронных сетей",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем REST API
app.include_router(rest_router, prefix="/api", tags=["api"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time коммуникации."""
    try:
        await websocket_hub.connect(websocket)
        
        # Ожидаем сообщения от клиента
        while True:
            try:
                data = await websocket.receive_text()
                # Обрабатываем входящие сообщения если нужно
                logger.debug(f"Получено WebSocket сообщение: {data}")
                
            except WebSocketDisconnect:
                websocket_hub.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"Ошибка WebSocket: {e}")
                break
                
    except Exception as e:
        logger.error(f"Ошибка WebSocket соединения: {e}")
        websocket_hub.disconnect(websocket)


# Главная страница
@app.get("/")
async def root():
    """Главная страница API."""
    return {
        "message": "🧠 Brainzzz API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    ) 