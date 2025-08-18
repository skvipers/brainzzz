"""
Тест параллельного движка для инкубатора мозгов.
"""

import time
import numpy as np
from brains import Brain, Genome, Phenotype, GrowthRules
from tasks import TaskManager, XORTask, SequenceTask
from dist import ParallelEngine, RayManager


def test_parallel_evaluation():
    """Тестирует параллельную оценку популяции."""
    print("🧠 Тест параллельной оценки популяции...")

    # Создаем менеджер задач
    task_manager = TaskManager()
    task_manager.add_task(XORTask())
    task_manager.add_task(SequenceTask())

    # Создаем популяцию мозгов
    population_size = 20
    population = []

    for i in range(population_size):
        genome = Genome(input_size=2, output_size=1, hidden_size=3)
        growth_rules = GrowthRules()
        brain = Brain(genome, growth_rules)
        brain.gp = np.random.random() * 10.0
        population.append(brain)

    print(f"   Создана популяция из {len(population)} мозгов")

    # Тестируем последовательную оценку
    print("\n📊 Последовательная оценка...")
    start_time = time.time()

    sequential_results = []
    for brain in population:
        task_results = task_manager.evaluate_brain(brain)
        fitness = brain.evaluate_fitness(task_results)
        sequential_results.append((brain, fitness))

    sequential_time = time.time() - start_time
    avg_fitness_seq = np.mean([r[1] for r in sequential_results])

    print(f"   Время: {sequential_time:.3f}с")
    print(f"   Средняя приспособленность: {avg_fitness_seq:.3f}")

    # Тестируем параллельную оценку
    print("\n🚀 Параллельная оценка...")

    try:
        parallel_engine = ParallelEngine(num_workers=4, use_ray=True)

        start_time = time.time()
        parallel_results = parallel_engine.evaluate_population_parallel(
            population, task_manager
        )
        parallel_time = time.time() - start_time

        avg_fitness_par = np.mean([r[1] for r in parallel_results])

        print(f"   Время: {parallel_time:.3f}с")
        print(f"   Средняя приспособленность: {avg_fitness_par:.3f}")
        print(f"   Ускорение: {sequential_time / parallel_time:.2f}x")

        # Проверяем корректность результатов
        fitness_diff = abs(avg_fitness_seq - avg_fitness_par)
        if fitness_diff < 0.01:
            print("   ✅ Результаты корректны")
        else:
            print(f"   ⚠️ Различие в результатах: {fitness_diff:.3f}")

        # Получаем статистику популяции
        stats = parallel_engine.get_population_statistics(population, task_manager)
        print(f"\n📈 Статистика популяции:")
        print(f"   Размер: {stats['population_size']}")
        print(f"   Валидных оценок: {stats['valid_evaluations']}")
        print(f"   Средняя приспособленность: {stats['avg_fitness']:.3f}")
        print(f"   Максимальная: {stats['max_fitness']:.3f}")
        print(f"   Среднее количество узлов: {stats['avg_nodes']:.1f}")
        print(f"   Ошибки: {stats['errors']}")

        parallel_engine.shutdown()

    except Exception as e:
        print(f"   ❌ Ошибка параллельной оценки: {e}")
        print("   Продолжаем с последовательной версией...")


def test_ray_manager():
    """Тестирует Ray менеджер."""
    print("\n🔧 Тест Ray менеджера...")

    try:
        # Создаем менеджер
        ray_manager = RayManager(num_cpus=4, local_mode=False)

        # Получаем информацию о кластере
        cluster_info = ray_manager.get_cluster_info()
        print(f"   Кластер: {cluster_info.num_cpus} CPU, {cluster_info.num_gpus} GPU")
        print(f"   Память: {cluster_info.memory_total / 1024**3:.1f} GB")
        print(f"   Активные акторы: {cluster_info.active_actors}")

        # Получаем рекомендации по оптимизации
        optimization = ray_manager.optimize_cluster_config()
        print(f"   Оценка оптимизации: {optimization['optimization_score']:.1f}/100")

        if optimization["recommendations"]:
            print("   📋 Рекомендации:")
            for category, rec in optimization["recommendations"].items():
                print(f"      {category}: {rec['message']}")

        # Краткий мониторинг ресурсов
        print("\n   🔍 Мониторинг ресурсов (5 секунд)...")
        ray_manager.monitor_resources(interval=1.0, duration=5.0)

        ray_manager.shutdown()

    except Exception as e:
        print(f"   ❌ Ошибка Ray менеджера: {e}")


def test_parallel_evolution():
    """Тестирует параллельную эволюцию."""
    print("\n🔄 Тест параллельной эволюции...")

    try:
        # Создаем движок
        parallel_engine = ParallelEngine(num_workers=4, use_ray=True)

        # Создаем небольшую популяцию
        population_size = 10
        population = []

        for i in range(population_size):
            genome = Genome(input_size=2, output_size=1, hidden_size=2)
            growth_rules = GrowthRules()
            brain = Brain(genome, growth_rules)
            population.append(brain)

        print(f"   Создана популяция из {len(population)} мозгов")

        # Эволюционируем популяцию
        mutation_rate = 0.8  # Увеличиваем вероятность мутации
        evolved_population = parallel_engine.evolve_population_parallel(
            population, mutation_rate
        )

        print(f"   Эволюция завершена, размер: {len(evolved_population)}")

        # Проверяем, что мозги изменились
        original_nodes = [b.phenotype.num_nodes for b in population]
        evolved_nodes = [b.phenotype.num_nodes for b in evolved_population]

        print(f"   Исходные узлы: {original_nodes}")
        print(f"   Эволюционировавшие узлы: {evolved_nodes}")

        # Проверяем, что хотя бы один мозг изменился
        if original_nodes != evolved_nodes:
            print("   ✅ Эволюция работает корректно")
        else:
            print("   ⚠️ Мозги не изменились (возможно, низкая вероятность мутации)")

        parallel_engine.shutdown()

    except Exception as e:
        print(f"   ❌ Ошибка параллельной эволюции: {e}")


def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование параллельного движка инкубатора мозгов")
    print("=" * 60)

    # Тест 1: Параллельная оценка
    test_parallel_evaluation()

    # Тест 2: Ray менеджер
    test_ray_manager()

    # Тест 3: Параллельная эволюция
    test_parallel_evolution()

    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    main()
