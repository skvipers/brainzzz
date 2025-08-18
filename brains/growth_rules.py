"""
Правила роста и развития мозга.
"""

import secrets
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# from .brain import Brain  # Циклический импорт


@dataclass
class GrowthRule:
    """Правило роста."""

    name: str
    cost: float  # Стоимость в GP
    probability: float  # Вероятность выбора
    min_gp: float  # Минимальное количество GP для применения
    max_nodes: int  # Максимальное количество узлов для применения


class GrowthRules:
    """
    Управляет правилами роста и развития мозга.

    Определяет:
    - Когда мозг может расти
    - Какие типы роста доступны
    - Стоимость различных операций роста
    """

    def __init__(self):
        # Базовые правила роста
        self.growth_rules = [
            GrowthRule(
                "add_node", cost=10.0, probability=0.4, min_gp=10.0, max_nodes=50
            ),
            GrowthRule(
                "split_node", cost=15.0, probability=0.3, min_gp=15.0, max_nodes=40
            ),
            GrowthRule(
                "add_connection", cost=5.0, probability=0.3, min_gp=5.0, max_nodes=100
            ),
        ]

        # Глобальные ограничения
        self.max_nodes = 100
        self.max_connections = 500
        self.growth_cost = 5.0  # Минимальная стоимость роста

        # Параметры роста
        self.growth_probability = 0.1  # Вероятность роста на шаге
        self.complexity_penalty = 0.01  # Штраф за сложность

    def select_growth_type(self, brain) -> Optional[str]:
        """
        Выбирает тип роста для мозга.

        Args:
            brain: Мозг для роста

        Returns:
            Тип роста или None, если рост невозможен
        """
        # Проверяем, может ли мозг расти
        if not self._can_grow(brain):
            return None

        # Фильтруем доступные правила
        available_rules = [
            rule
            for rule in self.growth_rules
            if (brain.gp >= rule.min_gp and brain.phenotype.num_nodes < rule.max_nodes)
        ]

        if not available_rules:
            return None

        # Выбираем правило на основе вероятностей
        total_probability = sum(rule.probability for rule in available_rules)
        if total_probability == 0:
            return None

        # Нормализуем вероятности
        normalized_rules = []
        cumulative_prob = 0.0

        for rule in available_rules:
            cumulative_prob += rule.probability / total_probability
            normalized_rules.append((rule, cumulative_prob))

        # Выбираем правило
        rand_val = secrets.randbelow(int(total_probability * 1000000)) / 1000000.0
        for rule, prob in normalized_rules:
            if rand_val <= prob:
                return rule.name

        return available_rules[-1].name

    def _can_grow(self, brain) -> bool:
        """
        Проверяет, может ли мозг расти.

        Args:
            brain: Мозг для проверки

        Returns:
            True, если мозг может расти
        """
        # Проверяем базовые условия
        if brain.gp < self.growth_cost:
            return False

        if brain.phenotype.num_nodes >= self.max_nodes:
            return False

        # Проверяем сложность
        if self._get_complexity_score(brain) > 0.8:
            return False

        # Случайная проверка для предотвращения слишком частого роста
        return secrets.randbelow(1000000) / 1000000.0 < self.growth_probability

    def _get_complexity_score(self, brain) -> float:
        """
        Вычисляет оценку сложности мозга.

        Args:
            brain: Мозг для оценки

        Returns:
            Оценка сложности (0.0 - 1.0)
        """
        phenotype = brain.phenotype

        # Количество узлов (нормализованное)
        node_complexity = phenotype.num_nodes / self.max_nodes

        # Плотность сети
        density_complexity = phenotype.get_network_density()

        # Средняя длина пути (нормализованная)
        path_complexity = min(phenotype.get_average_path_length() / 10.0, 1.0)

        # Взвешенная сумма
        complexity = (
            0.4 * node_complexity + 0.3 * density_complexity + 0.3 * path_complexity
        )

        return complexity

    def apply_growth_penalty(self, brain):
        """
        Применяет штраф за сложность.

        Args:
            brain: Мозг для штрафа
        """
        complexity_score = self._get_complexity_score(brain)
        if complexity_score > 0.5:
            penalty = (complexity_score - 0.5) * self.complexity_penalty
            brain.gp = max(0.0, brain.gp - penalty)

    def get_growth_cost(self, growth_type: str) -> float:
        """
        Возвращает стоимость конкретного типа роста.

        Args:
            growth_type: Тип роста

        Returns:
            Стоимость в GP
        """
        for rule in self.growth_rules:
            if rule.name == growth_type:
                return rule.cost
        return self.growth_cost

    def can_apply_growth(self, brain, growth_type: str) -> bool:
        """
        Проверяет, может ли быть применён конкретный тип роста.

        Args:
            brain: Мозг для проверки
            growth_type: Тип роста

        Returns:
            True, если рост может быть применён
        """
        for rule in self.growth_rules:
            if rule.name == growth_type:
                return (
                    brain.gp >= rule.min_gp
                    and brain.phenotype.num_nodes < rule.max_nodes
                )
        return False

    def get_available_growth_types(self, brain) -> List[str]:
        """
        Возвращает список доступных типов роста.

        Args:
            brain: Мозг для проверки

        Returns:
            Список доступных типов роста
        """
        available = []
        for rule in self.growth_rules:
            if self.can_apply_growth(brain, rule.name):
                available.append(rule.name)
        return available

    def optimize_growth_strategy(self, brain) -> Optional[str]:
        """
        Выбирает оптимальную стратегию роста.

        Args:
            brain: Мозг для оптимизации

        Returns:
            Оптимальный тип роста или None
        """
        available_types = self.get_available_growth_types(brain)
        if not available_types:
            return None

        # Простая эвристика: выбираем тип с наименьшей стоимостью
        # при достаточном количестве GP
        best_type = None
        best_ratio = 0.0

        for growth_type in available_types:
            cost = self.get_growth_cost(growth_type)
            if cost > 0:
                ratio = brain.gp / cost
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_type = growth_type

        return best_type

    def add_custom_growth_rule(self, rule: GrowthRule):
        """
        Добавляет пользовательское правило роста.

        Args:
            rule: Новое правило роста
        """
        self.growth_rules.append(rule)

    def remove_growth_rule(self, rule_name: str):
        """
        Удаляет правило роста.

        Args:
            rule_name: Название правила для удаления
        """
        self.growth_rules = [
            rule for rule in self.growth_rules if rule.name != rule_name
        ]

    def update_growth_parameters(self, **kwargs):
        """
        Обновляет параметры роста.

        Args:
            **kwargs: Параметры для обновления
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_growth_statistics(self, brain) -> Dict[str, Any]:
        """
        Возвращает статистику роста для мозга.

        Args:
            brain: Мозг для анализа

        Returns:
            Словарь со статистикой
        """
        return {
            "can_grow": self._can_grow(brain),
            "available_growth_types": self.get_available_growth_types(brain),
            "complexity_score": self._get_complexity_score(brain),
            "growth_probability": self.growth_probability,
            "max_nodes": self.max_nodes,
            "current_nodes": brain.phenotype.num_nodes,
            "gp_balance": brain.gp,
            "optimal_growth": self.optimize_growth_strategy(brain),
        }

    def __repr__(self):
        return (
            f"GrowthRules(rules={len(self.growth_rules)}, "
            f"max_nodes={self.max_nodes}, "
            f"growth_cost={self.growth_cost})"
        )
