"""
Основной класс для представления когнитивной структуры (мозга).
"""

from dataclasses import dataclass, field

import numpy as np

from .genome import Genome
from .growth_rules import GrowthRules
from .phenotype import Phenotype


@dataclass
class BrainState:
    """Состояние мозга в конкретный момент времени."""

    activations: np.ndarray  # Активации всех узлов
    memory: dict = field(default_factory=dict)  # Кратковременная память
    step_count: int = 0  # Счётчик шагов
    last_commit: int = 0  # Последний шаг commit


class Brain:
    """
    Когнитивная структура, способная расти и эволюционировать.

    Атрибуты:
        genome: Генетическая информация
        phenotype: Фенотипическое представление
        growth_rules: Правила роста и развития
        gp: Очки развития (Growth Points)
        fitness: Приспособленность
        age: Возраст мозга
        state: Текущее состояние
    """

    def __init__(self, genome: Genome, growth_rules: GrowthRules):
        self.genome = genome
        self.growth_rules = growth_rules
        self.phenotype = Phenotype(genome)
        self.gp = 0.0  # Growth Points
        self.fitness = 0.0
        self.age = 0
        self.state = BrainState(activations=np.zeros(self.phenotype.num_nodes))
        self.history = []  # История состояний для анализа

    def process_input(self, input_data: np.ndarray) -> np.ndarray:
        """
        Обрабатывает входные данные и возвращает выход.

        Args:
            input_data: Входные данные

        Returns:
            Выходные данные
        """
        # Обновляем активации входных узлов
        self.state.activations[: len(input_data)] = input_data

        # Выполняем один шаг обработки
        self._step()

        # Возвращаем выходные активации
        return self.phenotype.get_output_activations(self.state.activations)

    def _step(self):
        """Выполняет один шаг обработки."""
        # Применяем правила активации
        new_activations = self.phenotype.compute_activations(self.state.activations)

        # Обновляем состояние
        self.state.activations = new_activations
        self.state.step_count += 1

        # Сохраняем историю
        self.history.append(self.state.activations.copy())

        # Проверяем возможность роста
        if self._can_grow():
            self._grow()

    def _can_grow(self) -> bool:
        """Проверяет, может ли мозг расти."""
        return (
            self.gp >= self.growth_rules.growth_cost
            and self.phenotype.num_nodes < self.growth_rules.max_nodes
        )

    def _grow(self):
        """Выполняет рост мозга."""
        growth_type = self.growth_rules.select_growth_type(self)

        if growth_type == "add_node":
            self._add_node()
        elif growth_type == "split_node":
            self._split_node()
        elif growth_type == "add_connection":
            self._add_connection()

        # Тратим GP на рост
        self.gp -= self.growth_rules.growth_cost

    def _add_node(self):
        """Добавляет новый узел."""
        # Создаем новый узел в геноме
        self.genome.add_node()

        # Обновляем фенотип
        self.phenotype = Phenotype(self.genome)

        # Расширяем состояние
        old_activations = self.state.activations
        self.state.activations = np.zeros(self.phenotype.num_nodes)
        self.state.activations[: len(old_activations)] = old_activations

        # logger.info(f"Добавлен новый узел: {new_node.id}")

    def _split_node(self):
        """Разделяет существующий узел."""
        # Выбираем узел для разделения
        target_node = self.growth_rules.select_node_for_splitting(self)

        if target_node:
            # Разделяем узел в геноме
            new_nodes = self.genome.split_node(target_node.id)

            # Обновляем фенотип
            self.phenotype = Phenotype(self.genome)

            # Обновляем состояние
            self._update_state_after_splitting(target_node, new_nodes)

            # logger.info(f"Узел {target_node.id} разделен на {len(new_nodes)} узлов")

    def _add_connection(self):
        """Добавляет новое соединение."""
        # Выбираем узлы для соединения
        from_node, to_node = self.growth_rules.select_connection_endpoints(self)

        if from_node and to_node:
            # Добавляем соединение в геном
            self.genome.add_connection(from_node.id, to_node.id)

            # Обновляем фенотип
            self.phenotype = Phenotype(self.genome)

            # logger.info(f"Добавлено соединение: {from_node.id} -> {to_node.id}")

    def _update_state_after_splitting(self, old_node, new_nodes):
        """Обновляет состояние после разделения узла."""
        # Копируем активацию старого узла на новые узлы
        old_activation = self.state.activations[old_node.id]

        # Расширяем массив активаций
        old_size = len(self.state.activations)
        new_size = old_size + len(new_nodes) - 1
        new_activations = np.zeros(new_size)

        # Копируем старые активации
        new_activations[:old_size] = self.state.activations

        # Распределяем активацию старого узла на новые
        for i, new_node in enumerate(new_nodes):
            new_activations[new_node.id] = old_activation / len(new_nodes)

        self.state.activations = new_activations

    def get_fitness(self) -> float:
        """Возвращает текущую приспособленность."""
        return self.fitness

    def set_fitness(self, fitness: float):
        """Устанавливает приспособленность."""
        self.fitness = fitness

    def get_gp(self) -> float:
        """Возвращает текущие очки развития."""
        return self.gp

    def add_gp(self, amount: float):
        """Добавляет очки развития."""
        self.gp += amount

    def get_age(self) -> int:
        """Возвращает возраст мозга."""
        return self.age

    def increment_age(self):
        """Увеличивает возраст мозга."""
        self.age += 1

    def clone(self) -> "Brain":
        """Создает копию мозга."""
        cloned_brain = Brain(
            genome=self.genome.clone(), growth_rules=self.growth_rules.clone()
        )
        cloned_brain.gp = self.gp
        cloned_brain.fitness = self.fitness
        cloned_brain.age = self.age
        return cloned_brain

    def __repr__(self):
        return (
            f"Brain(nodes={self.phenotype.num_nodes}, "
            f"connections={len(self.genome.connection_genes)}, "
            f"fitness={self.fitness:.3f}, gp={self.gp:.3f}, age={self.age})"
        )
