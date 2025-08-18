"""
Тестовый скрипт для проверки Brainzzz API.
"""

import asyncio
import aiohttp


async def test_api():
    """Тестируем API endpoints."""

    async with aiohttp.ClientSession() as session:
        base_url = "http://localhost:8000"

        print("🧪 Тестируем Brainzzz API...")

        # Тест главной страницы
        try:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Главная страница: {data['message']}")
                else:
                    print(f"❌ Главная страница: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка главной страницы: {e}")

        # Тест health check
        try:
            async with session.get(f"{base_url}/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data['status']}")
                else:
                    print(f"❌ Health check: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка health check: {e}")

        # Тест статуса системы
        try:
            async with session.get(f"{base_url}/api/v1/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Статус системы: {data['status']}")
                    print(f"   Redis: {data['connections']['redis']}")
                    print(f"   DuckDB: {data['connections']['duckdb']}")
                else:
                    print(f"❌ Статус системы: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка статуса системы: {e}")

        # Тест статистики популяции
        try:
            async with session.get(f"{base_url}/api/v1/population/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Статистика популяции: {data['count']} записей")
                else:
                    print(f"❌ Статистика популяции: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка статистики популяции: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
