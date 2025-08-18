"""
Основной движок эволюции для популяции мозгов.
"""

import secrets
from typing import Any, Dict, List

import numpy as np

from brains import Brain

from .crossover import Crossover
from .mutation import Mutation
from .selection import Selection


class EvolutionEngine:
    """
    Движок эволюции, управляющий популяцией мозгов.

    Функции:
    - Селекция лучших особей
    - Скрещивание для создания потомков
    - Мутации для разнообразия
    - Управление размером популяции
    """

    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 5,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size

        # Компоненты эволюции
        self.selection = Selection()
        self.mutation = Mutation()
        self.crossover = Crossover()

        # История эволюции
        self.generation_history: List[Dict[str, Any]] = []
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []

    def evolve_population(self, population: List[Brain]) -> List[Brain]:
        """
        Эволюционирует популяцию на одно поколение.

        Args:
            population: Текущая популяция

        Returns:
            Новая популяция
        """
        if len(population) < 2:
            return population

        # Сохраняем историю
        self._save_generation_stats(population)

        # Сортируем по приспособленности
        population.sort(key=lambda brain: brain.fitness, reverse=True)

        # Элитизм: сохраняем лучших
        new_population = population[: self.elite_size].copy()

        # Создаём потомков
        while len(new_population) < self.population_size:
            # Селекция родителей
            parent1 = self.selection.select_parent(population)
            parent2 = self.selection.select_parent(population)

            # Скрещивание
            if secrets.randbelow(2) < self.crossover_rate:
                offspring = self.crossover.crossover(parent1, parent2)
            else:
                offspring = parent1.clone()

            # Мутация
            if secrets.randbelow(2) < self.mutation_rate:
                self.mutation.mutate(offspring)

            # Сброс приспособленности для нового потомка
            offspring.fitness = 0.0
            # Увеличиваем возраст потомка
            offspring.age = parent1.age + 1

            new_population.append(offspring)

        # Обрезаем до нужного размера
        new_population = new_population[: self.population_size]

        return new_population

    def _save_generation_stats(self, population: List[Brain]):
        """Сохраняет статистику поколения."""
        if not population:
            return

        fitness_scores = [brain.fitness for brain in population]

        stats = {
            "generation": len(self.generation_history) + 1,
            "population_size": len(population),
            "best_fitness": max(fitness_scores),
            "avg_fitness": np.mean(fitness_scores),
            "worst_fitness": min(fitness_scores),
            "fitness_std": np.std(fitness_scores),
            "best_brain": max(population, key=lambda b: b.fitness),
        }

        self.generation_history.append(stats)
        self.best_fitness_history.append(stats["best_fitness"])
        self.avg_fitness_history.append(stats["avg_fitness"])

        # Ограничиваем размер истории
        if len(self.generation_history) > 1000:
            self.generation_history = self.generation_history[-1000:]
            self.best_fitness_history = self.best_fitness_history[-1000:]
            self.avg_fitness_history = self.avg_fitness_history[-1000:]

    def get_evolution_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику эволюции.

        Returns:
            Словарь со статистикой
        """
        if not self.generation_history:
            return {}

        latest = self.generation_history[-1]

        stats = {
            "total_generations": len(self.generation_history),
            "current_population_size": latest["population_size"],
            "best_fitness_ever": max(self.best_fitness_history),
            "current_best_fitness": latest["best_fitness"],
            "current_avg_fitness": latest["avg_fitness"],
            "fitness_improvement": (
                (self.best_fitness_history[-1] - self.best_fitness_history[0])
                if len(self.best_fitness_history) > 1
                else 0.0
            ),
            "convergence_rate": self._calculate_convergence_rate(),
        }

        return stats

    def _calculate_convergence_rate(self) -> float:
        """Вычисляет скорость сходимости эволюции."""
        if len(self.best_fitness_history) < 10:
            return 0.0

        # Вычисляем среднее изменение приспособленности за последние 10 поколений
        recent_changes = []
        for i in range(1, min(10, len(self.best_fitness_history))):
            change = self.best_fitness_history[-i] - self.best_fitness_history[-i - 1]
            recent_changes.append(change)

        return np.mean(recent_changes)

    def get_best_brain(self, population: List[Brain]) -> Any:
        """
        Возвращает лучший мозг из популяции.

        Args:
            population: Популяция мозгов

        Returns:
            Лучший мозг или None
        """
        if not population:
            return None

        return max(population, key=lambda brain: brain.fitness)

    def get_diversity_score(self, population: List[Brain]) -> float:
        """
        Вычисляет оценку разнообразия популяции.

        Args:
            population: Популяция мозгов

        Returns:
            Оценка разнообразия (0.0 - 1.0)
        """
        if len(population) < 2:
            return 0.0

        # Вычисляем разнообразие на основе структурных характеристик
        node_counts = [brain.phenotype.num_nodes for brain in population]
        gp_values = [brain.gp for brain in population]

        # Нормализуем значения
        node_std = np.std(node_counts) / max(1, np.mean(node_counts))
        gp_std = np.std(gp_values) / max(1, np.mean(gp_values))

        # Общая оценка разнообразия
        diversity = (node_std + gp_std) / 2.0

        return min(1.0, diversity)

    def adjust_parameters(self, population: List[Brain], target_diversity: float = 0.3):
        """
        Автоматически настраивает параметры эволюции.

        Args:
            population: Текущая популяция
            target_diversity: Целевое разнообразие
        """
        current_diversity = self.get_diversity_score(population)

        if current_diversity < target_diversity * 0.5:
            # Слишком мало разнообразия - увеличиваем мутации
            self.mutation_rate = min(0.3, self.mutation_rate * 1.2)
            self.crossover_rate = max(0.5, self.crossover_rate * 0.9)
        elif current_diversity > target_diversity * 1.5:
            # Слишком много разнообразия - уменьшаем мутации
            self.mutation_rate = max(0.05, self.mutation_rate * 0.8)
            self.crossover_rate = min(0.9, self.crossover_rate * 1.1)

    def reset_history(self):
        """Сбрасывает историю эволюции."""
        self.generation_history.clear()
        self.best_fitness_history.clear()
        self.avg_fitness_history.clear()

    def __repr__(self):
        return (
            f"EvolutionEngine(pop_size={self.population_size}, "
            f"mutation_rate={self.mutation_rate:.2f}, "
            f"crossover_rate={self.crossover_rate:.2f}, "
            f"elite_size={self.elite_size})"
        )
