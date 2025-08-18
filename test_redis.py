#!/usr/bin/env python3
"""
Тест Redis интеграции для Brainzzz.
"""

import asyncio

from web.event_bus import event_bus
from web.redis_manager import redis_manager


async def test_redis_connection():
    """Тестирует подключение к Redis."""
    print("🔴 Тестирование Redis подключения...")

    try:
        # Подключаемся к Redis
        connected = await redis_manager.connect()
        if connected:
            print("✅ Redis подключен успешно!")

            # Получаем статистику
            stats = await redis_manager.get_system_stats()
            print("📊 Статистика Redis:")
            print(f"   Версия: {stats.get('redis_version', 'N/A')}")
            print(f"   Клиенты: {stats.get('connected_clients', 'N/A')}")
            print(f"   Память: {stats.get('used_memory_human', 'N/A')}")

            # Тестируем публикацию события
            success = await redis_manager.publish_event(
                "test", {"message": "Hello Redis!"}
            )
            if success:
                print("✅ Событие успешно отправлено в Redis")
            else:
                print("❌ Ошибка отправки события")

        else:
            print("❌ Не удалось подключиться к Redis")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def test_event_bus():
    """Тестирует Event Bus."""
    print("\n🚀 Тестирование Event Bus...")

    try:
        # Запускаем Event Bus
        await event_bus.start()
        print("✅ Event Bus запущен")

        # Тестируем публикацию события
        await event_bus.publish_population_tick(
            generation=1, population_size=20, best_fitness=0.8, mean_fitness=0.6
        )
        print("✅ Событие популяции отправлено")

        # Останавливаем Event Bus
        await event_bus.stop()
        print("✅ Event Bus остановлен")

    except Exception as e:
        print(f"❌ Ошибка Event Bus: {e}")


async def test_integration():
    """Тестирует полную интеграцию."""
    print("\n🔗 Тестирование полной интеграции...")

    try:
        # Подключаемся к Redis
        await redis_manager.connect()

        # Запускаем Event Bus
        await event_bus.start()

        # Публикуем несколько событий
        await event_bus.publish_brain_snapshot(1, {"nodes": 10, "fitness": 0.7})
        await event_bus.publish_growth_event(1, "add_node", {"cost": 5.0})
        await event_bus.publish_help_score(1, 0.3, "cooperation", 2)

        print("✅ Все события отправлены")

        # Останавливаем
        await event_bus.stop()
        await redis_manager.disconnect()

    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")


async def main():
    """Главная функция."""
    print("🧠 Тестирование Redis интеграции для Brainzzz\n")

    # Тест 1: Redis подключение
    await test_redis_connection()

    # Тест 2: Event Bus
    await test_event_bus()

    # Тест 3: Полная интеграция
    await test_integration()

    print("\n✨ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
