"""
Тестовый файл для проверки WebSocket endpoint.
"""

import asyncio
import websockets


async def test_websocket():
    """Тестируем WebSocket соединение."""
    try:
        print("🔌 Подключаюсь к WebSocket...")
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            print("✅ WebSocket соединение установлено!")

            # Отправляем тестовое сообщение
            await websocket.send("Hello from test!")
            print("📤 Сообщение отправлено")

            # Ждем ответа
            response = await websocket.recv()
            print(f"📨 Получен ответ: {response}")

    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
