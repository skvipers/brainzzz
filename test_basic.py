#!/usr/bin/env python3
"""
Простой тест базовой функциональности инкубатора мозгов.
"""

import numpy as np

from brains import Brain, Genome, GrowthRules
from tasks import SequenceTask, TaskManager, XORTask


def test_basic_functionality():
    """Тестирует базовую функциональность."""
    print("🧠 Тестирование базовой функциональности инкубатора мозгов...")

    # Создаём компоненты
    print("1. Создание компонентов...")
    genome = Genome(input_size=2, output_size=1, hidden_size=3)
    growth_rules = GrowthRules()
    brain = Brain(genome, growth_rules)

    print(f"   Создан мозг: {brain}")
    print(f"   Узлы: {brain.phenotype.num_nodes}")
    print(f"   Соединения: {len(brain.genome.connection_genes)}")

    # Тестируем обработку входов
    print("\n2. Тестирование обработки входов...")
    test_inputs = [
        np.array([0.0, 0.0]),
        np.array([0.0, 1.0]),
        np.array([1.0, 0.0]),
        np.array([1.0, 1.0]),
    ]

    for i, input_data in enumerate(test_inputs):
        output = brain.process_input(input_data)
        print(f"   Вход {input_data} -> Выход {output}")

    # Тестируем задачи
    print("\n3. Тестирование задач...")
    task_manager = TaskManager()
    task_manager.add_task(XORTask())
    task_manager.add_task(SequenceTask())

    # Оцениваем мозг
    task_results = task_manager.evaluate_brain(brain)
    fitness = brain.evaluate_fitness(task_results)

    print(f"   Результаты задач: {task_results}")
    print(f"   Приспособленность: {fitness:.3f}")
    print(f"   GP: {brain.gp:.2f}")

    # Тестируем рост
    print("\n4. Тестирование роста...")
    print(f"   Может расти: {brain.growth_rules._can_grow(brain)}")
    print(
        f"   Доступные типы роста: "
        f"{brain.growth_rules.get_available_growth_types(brain)}"
    )

    # Даём GP для роста
    brain.gp = 20.0
    print(f"   Увеличили GP до: {brain.gp:.2f}")
    print(f"   Теперь может расти: {brain.growth_rules._can_grow(brain)}")

    # Тестируем мутации
    print("\n5. Тестирование мутаций...")
    old_weights = [conn.weight for conn in brain.genome.connection_genes]
    brain.mutate(mutation_rate=0.3)
    new_weights = [conn.weight for conn in brain.genome.connection_genes]

    print(f"   Веса до мутации: {[f'{w:.3f}' for w in old_weights]}")
    print(f"   Веса после мутации: {[f'{w:.3f}' for w in new_weights]}")

    # Тестируем клонирование
    print("\n6. Тестирование клонирования...")
    brain_clone = brain.clone()
    print(f"   Оригинал: {brain}")
    print(f"   Клон: {brain_clone}")
    print(f"   Клон имеет GP: {brain_clone.gp:.2f}")

    print("\n✅ Базовое тестирование завершено успешно!")


def test_evolution():
    """Тестирует простую эволюцию."""
    print("\n🔄 Тестирование простой эволюции...")

    # Создаём популяцию
    population_size = 5
    brains = []
    growth_rules = GrowthRules()

    for i in range(population_size):
        genome = Genome(
            input_size=np.random.randint(2, 4),
            output_size=np.random.randint(1, 3),
            hidden_size=np.random.randint(2, 5),
        )
        brain = Brain(genome, growth_rules)
        brain.gp = np.random.uniform(5.0, 15.0)
        brains.append(brain)

    print(f"   Создана популяция из {len(brains)} мозгов")

    # Оцениваем популяцию
    task_manager = TaskManager()
    task_manager.add_task(XORTask())

    print("   Оценка популяции...")
    for i, brain in enumerate(brains):
        task_results = task_manager.evaluate_brain(brain)
        fitness = brain.evaluate_fitness(task_results)
        print(f"     Мозг {i+1}: fitness={fitness:.3f}, GP={brain.gp:.2f}")

    # Находим лучшего
    best_brain = max(brains, key=lambda b: b.fitness)
    print(f"   Лучший мозг: fitness={best_brain.fitness:.3f}")

    # Простая эволюция: мутируем худших
    print("   Мутация худших особей...")
    brains.sort(key=lambda b: b.fitness)
    worst_brains = brains[:2]

    for brain in worst_brains:
        old_fitness = brain.fitness
        brain.mutate(mutation_rate=0.5)
        print(f"     Мутировал мозг: {old_fitness:.3f} -> {brain.fitness:.3f}")

    print("✅ Тестирование эволюции завершено!")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_evolution()
        print("\n🎉 Все тесты пройдены успешно!")

    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()
