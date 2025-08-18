"""
Стратегии селекции для эволюционного алгоритма.
"""

import random
from typing import List
from brains import Brain


class Selection:
    """
    Управляет стратегиями селекции родителей для эволюции.

    Доступные стратегии:
    - Tournament: турнирная селекция
    - Roulette: рулеточная селекция
    - Rank: ранжированная селекция
    """

    def __init__(self, strategy: str = "tournament"):
        self.strategy = strategy
        self.tournament_size = 3

    def select_parent(self, population: List[Brain]) -> Brain:
        """
        Выбирает родителя из популяции.

        Args:
            population: Популяция мозгов

        Returns:
            Выбранный родитель
        """
        if self.strategy == "tournament":
            return self._tournament_selection(population)
        elif self.strategy == "roulette":
            return self._roulette_selection(population)
        elif self.strategy == "rank":
            return self._rank_selection(population)
        else:
            return self._tournament_selection(population)

    def _tournament_selection(self, population: List[Brain]) -> Brain:
        """Турнирная селекция."""
        # Выбираем случайных участников турнира
        tournament = random.sample(
            population, min(self.tournament_size, len(population))
        )

        # Возвращаем лучшего из турнира
        return max(tournament, key=lambda brain: brain.fitness)

    def _roulette_selection(self, population: List[Brain]) -> Brain:
        """Рулеточная селекция (пропорциональная приспособленности)."""
        if not population:
            raise ValueError("Популяция пуста")

        # Вычисляем общую приспособленность
        total_fitness = sum(max(0.0, brain.fitness) for brain in population)

        if total_fitness <= 0:
            # Если все приспособленности нулевые, выбираем случайно
            return random.choice(population)

        # Выбираем случайную точку на рулетке
        rand_val = random.uniform(0, total_fitness)

        # Находим соответствующую особь
        current_sum = 0.0
        for brain in population:
            current_sum += max(0.0, brain.fitness)
            if current_sum >= rand_val:
                return brain

        # На всякий случай возвращаем последнюю особь
        return population[-1]

    def _rank_selection(self, population: List[Brain]) -> Brain:
        """Ранжированная селекция."""
        if not population:
            raise ValueError("Популяция пуста")

        # Сортируем по приспособленности
        sorted_population = sorted(population, key=lambda brain: brain.fitness)

        # Вычисляем веса на основе ранга
        n = len(sorted_population)
        weights = [2 * (n - i) / (n * (n + 1)) for i in range(n)]

        # Выбираем на основе весов
        rand_val = random.random()
        cumulative_weight = 0.0

        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if cumulative_weight >= rand_val:
                return sorted_population[i]

        return sorted_population[-1]

    def set_strategy(self, strategy: str):
        """Устанавливает стратегию селекции."""
        valid_strategies = ["tournament", "roulette", "rank"]
        if strategy in valid_strategies:
            self.strategy = strategy
        else:
            raise ValueError(
                f"Неизвестная стратегия: {strategy}. "
                f"Доступные: {valid_strategies}"
            )

    def set_tournament_size(self, size: int):
        """Устанавливает размер турнира."""
        if size >= 2:
            self.tournament_size = size
        else:
            raise ValueError("Размер турнира должен быть >= 2")

    def __repr__(self):
        return (
            f"Selection(strategy={self.strategy}, "
            f"tournament_size={self.tournament_size})"
        )
