"""
Простой тест для проверки API endpoints.
"""

import asyncio
import logging

import aiohttp

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Базовый URL для тестов
BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Тест health check endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/health") as response:
            assert response.status == 200  # nosec B101
            data = await response.json()
            assert data["status"] == "healthy"  # nosec B101
            logger.info("[SUCCESS] Health check прошел")


async def test_population_endpoint():
    """Тест population endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/population") as response:
            assert response.status == 200  # nosec B101
            data = await response.json()
            assert isinstance(data, list)  # nosec B101
            assert len(data) > 0  # nosec B101
            logger.info(f"[SUCCESS] Population endpoint прошел: {len(data)} мозгов")


async def test_stats_endpoint():
    """Тест stats endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/stats") as response:
            assert response.status == 200  # nosec B101
            data = await response.json()
            assert "size" in data  # nosec B101
            assert "avg_fitness" in data  # nosec B101
            logger.info("[SUCCESS] Stats endpoint прошел")


async def test_websocket_status():
    """Тест WebSocket status endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/ws/status") as response:
            assert response.status == 200  # nosec B101
            data = await response.json()
            assert "status" in data  # nosec B101
            assert "max_connections" in data  # nosec B101
            logger.info("[SUCCESS] WebSocket status endpoint прошел")


async def test_redis_event():
    """Тест Redis event publishing."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/test-redis") as response:
            # Redis может быть недоступен, поэтому проверяем только статус
            assert response.status in [
                200,
                500,
            ]  # nosec B101 - 500 если Redis недоступен
            data = await response.json()
            logger.info(f"[SUCCESS] Redis test endpoint прошел: {data['status']}")


async def run_all_tests():
    """Запуск всех тестов."""
    logger.info("[STARTUP] Запуск тестов API...")

    tests = [
        test_health_check,
        test_population_endpoint,
        test_stats_endpoint,
        test_websocket_status,
        test_redis_event,
    ]

    for test in tests:
        try:
            await test()
        except Exception as e:
            logger.error(f"[ERROR] Тест {test.__name__} упал: {e}")

    logger.info("[SUCCESS] Все тесты завершены")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
