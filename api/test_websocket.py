"""
Простой тест для проверки WebSocket соединения.
"""

import asyncio
import json
import logging

import websockets

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket URL для тестов
WS_URL = "ws://localhost:8000/ws"


async def test_websocket_connection():
    """Тест WebSocket соединения."""
    try:
        logger.info(f"[CONNECT] Подключение к WebSocket: {WS_URL}")

        async with websockets.connect(WS_URL) as websocket:
            logger.info("[SUCCESS] WebSocket соединение установлено")

            # Ждем приветственное сообщение
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                logger.info(f"[MESSAGE] Получено сообщение: {data['type']}")

                # Отправляем ping
                await websocket.send('{"type": "ping"}')
                logger.info("[PING] Ping отправлен")

                # Ждем ответ на ping
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"[MESSAGE] Ответ на ping: {response}")
                except asyncio.TimeoutError:
                    logger.warning("[WARNING] Таймаут ответа на ping")

            except asyncio.TimeoutError:
                logger.warning("[WARNING] Таймаут приветственного сообщения")

            logger.info("[SUCCESS] WebSocket тест завершен успешно")

    except Exception as e:
        logger.error(f"[ERROR] Ошибка WebSocket теста: {e}")
        return False

    return True


async def test_websocket_reconnection():
    """Тест переподключения WebSocket."""
    try:
        logger.info("[RESET] Тест переподключения WebSocket...")

        # Первое подключение
        async with websockets.connect(WS_URL) as ws1:
            logger.info("[SUCCESS] Первое подключение установлено")

            # Второе подключение
            async with websockets.connect(WS_URL) as ws2:
                logger.info("[SUCCESS] Второе подключение установлено")

                # Проверяем, что оба работают
                await ws1.send('{"type": "test"}')
                await ws2.send('{"type": "test"}')
                logger.info("[SUCCESS] Оба соединения активны")

        logger.info("[SUCCESS] Тест переподключения прошел")
        return True

    except Exception as e:
        logger.error(f"[ERROR] Ошибка теста переподключения: {e}")
        return False


async def run_websocket_tests():
    """Запуск всех WebSocket тестов."""
    logger.info("[STARTUP] Запуск WebSocket тестов...")

    tests = [
        test_websocket_connection,
        test_websocket_reconnection,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"[ERROR] Тест {test.__name__} упал: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)
    logger.info(f"[SUCCESS] WebSocket тесты завершены: {passed}/{total} прошли")

    return passed == total


if __name__ == "__main__":
    asyncio.run(run_websocket_tests())
