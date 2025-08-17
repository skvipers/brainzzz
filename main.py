#!/usr/bin/env python3
"""
Основной файл для запуска эволюционного инкубатора мозгов.
"""

import numpy as np
import time
import logging
from typing import List, Dict, Any
from brains import Brain, Genome, GrowthRules
from tasks import TaskManager, XORTask, SequenceTask
from evo import EvolutionEngine
from viz import BrainVisualizer
from dist import ParallelEngine


def setup_logging():
    """Настраивает логирование."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('brain_incubator.log'),
            logging.StreamHandler()
        ]
    )


def create_initial_population(population_size: int = 10) -> List[Brain]:
    """
    Создаёт начальную популяцию мозгов.
    
    Args:
        population_size: Размер популяции
        
    Returns:
        Список мозгов
    """
    brains = []
    growth_rules = GrowthRules()
    
    for i in range(population_size):
        # Создаём геном с разными размерами
        input_size = np.random.randint(2, 5)
        output_size = np.random.randint(1, 3)
        hidden_size = np.random.randint(2, 6)
        
        genome = Genome(input_size, output_size, hidden_size)
        brain = Brain(genome, growth_rules)
        
        # Даём начальные GP для возможности роста
        brain.gp = np.random.uniform(5.0, 15.0)
        
        brains.append(brain)
        logging.info(f"Создан мозг {i+1}: {brain}")
    
    return brains


def run_evolution_cycle(brains: List[Brain], 
                        task_manager: TaskManager,
                        evolution_engine: EvolutionEngine,
                        num_generations: int = 100) -> List[Brain]:
    """
    Запускает основной цикл эволюции.
    
    Args:
        brains: Начальная популяция
        task_manager: Менеджер задач
        evolution_engine: Движок эволюции
        num_generations: Количество поколений
        
    Returns:
        Финальная популяция
    """
    current_population = brains.copy()
    
    for generation in range(num_generations):
        logging.info(f"\n=== Поколение {generation + 1}/{num_generations} ===")
        
        # Оцениваем приспособленность
        fitness_scores = []
        for brain in current_population:
            # Решаем задачи
            task_results = task_manager.evaluate_brain(brain)
            fitness = brain.evaluate_fitness(task_results)
            fitness_scores.append(fitness)
            
            logging.info(f"Мозг {brain}: fitness={fitness:.3f}, GP={brain.gp:.2f}")
        
        # Показываем статистику популяции
        avg_fitness = np.mean(fitness_scores)
        max_fitness = np.max(fitness_scores)
        avg_nodes = np.mean([b.phenotype.num_nodes for b in current_population])
        
        logging.info(f"Средняя приспособленность: {avg_fitness:.3f}")
        logging.info(f"Максимальная приспособленность: {max_fitness:.3f}")
        logging.info(f"Среднее количество узлов: {avg_nodes:.1f}")
        
        # Эволюционируем популяцию
        current_population = evolution_engine.evolve_population(current_population)
        
        # Проверяем условия остановки
        if max_fitness > 0.95:
            logging.info("Достигнута высокая приспособленность! Останавливаем эволюцию.")
            break
        
        # Небольшая пауза между поколениями
        time.sleep(0.1)
    
    return current_population


def main():
    """Основная функция."""
    print("🧠 Запуск инкубатора мозгов...")
    
    # Настраиваем логирование
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Создаём компоненты системы
        logger.info("Инициализация компонентов...")
        
        # Менеджер задач
        task_manager = TaskManager()
        task_manager.add_task(XORTask())
        task_manager.add_task(SequenceTask())
        
        # Движок эволюции
        evolution_engine = EvolutionEngine(
            population_size=10,
            mutation_rate=0.1,
            crossover_rate=0.7,
            elite_size=2
        )
        
        # Визуализатор
        visualizer = BrainVisualizer()
        
        # Создаём начальную популяцию
        logger.info("Создание начальной популяции...")
        initial_population = create_initial_population(population_size=10)
        
        # Запускаем эволюцию
        logger.info("Запуск эволюционного цикла...")
        final_population = run_evolution_cycle(
            brains=initial_population,
            task_manager=task_manager,
            evolution_engine=evolution_engine,
            num_generations=50
        )
        
        # Анализируем результаты
        logger.info("Анализ результатов...")
        best_brain = max(final_population, key=lambda b: b.fitness)
        
        logger.info(f"\n🏆 Лучший мозг:")
        logger.info(f"   Приспособленность: {best_brain.fitness:.3f}")
        logger.info(f"   Узлы: {best_brain.phenotype.num_nodes}")
        logger.info(f"   GP: {best_brain.gp:.2f}")
        logger.info(f"   Сложность: {best_brain.phenotype.get_network_density():.3f}")
        
        # Показываем путь мысли лучшего мозга
        thought_path = best_brain.get_thought_path()
        logger.info(f"   Путь мысли: {thought_path[:10]}...")  # Первые 10 шагов
        
        # Визуализируем лучший мозг
        logger.info("Создание визуализации...")
        visualizer.visualize_brain(best_brain, save_path="best_brain.png")
        
        print(f"\n✅ Эволюция завершена! Лучший мозг имеет приспособленность {best_brain.fitness:.3f}")
        
    except Exception as e:
        logger.error(f"Ошибка в основном цикле: {e}", exc_info=True)
        print(f"\n❌ Произошла ошибка: {e}")
        raise


if __name__ == "__main__":
    main() 