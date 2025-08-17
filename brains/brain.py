"""
Основной класс для представления когнитивной структуры (мозга).
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from .genome import Genome
from .phenotype import Phenotype
from .growth_rules import GrowthRules


@dataclass
class BrainState:
    """Состояние мозга в конкретный момент времени."""
    activations: np.ndarray  # Активации всех узлов
    memory: Dict[str, Any] = field(default_factory=dict)  # Кратковременная память
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
        self.state = BrainState(
            activations=np.zeros(self.phenotype.num_nodes)
        )
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
        self.state.activations[:len(input_data)] = input_data
        
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
        return (self.gp >= self.growth_rules.growth_cost and 
                self.phenotype.num_nodes < self.growth_rules.max_nodes)
    
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
        
        # Обновляем фенотип
        self.phenotype = Phenotype(self.genome)
        
        # Расширяем состояние
        old_activations = self.state.activations
        self.state.activations = np.zeros(self.phenotype.num_nodes)
        self.state.activations[:len(old_activations)] = old_activations
    
    def _add_node(self):
        """Добавляет новый узел."""
        # Логика добавления узла в геном
        pass
    
    def _split_node(self):
        """Разделяет существующий узел."""
        # Логика разделения узла
        pass
    
    def _add_connection(self):
        """Добавляет новое соединение."""
        # Логика добавления соединения
        pass
    
    def commit(self):
        """Фиксирует текущий выбор на несколько шагов."""
        self.state.last_commit = self.state.step_count
    
    def get_thought_path(self) -> List[int]:
        """Возвращает путь мысли (последовательность активированных узлов)."""
        if not self.history:
            return []
        
        # Находим узлы с максимальной активацией на каждом шаге
        thought_path = []
        for step_activations in self.history:
            max_node = np.argmax(step_activations)
            thought_path.append(max_node)
        
        return thought_path
    
    def evaluate_fitness(self, task_results: List[float]) -> float:
        """
        Оценивает приспособленность на основе результатов задач.
        
        Args:
            task_results: Список результатов выполнения задач
            
        Returns:
            Оценка приспособленности
        """
        if not task_results:
            return 0.0
        
        # Простая оценка: среднее по результатам
        self.fitness = np.mean(task_results)
        
        # Начисляем GP за успешное выполнение
        if self.fitness > 0.5:  # Порог успеха
            self.gp += self.fitness * 10.0
        else:
            # Даже при неудаче даем небольшое количество GP для возможности роста
            self.gp += max(0.1, self.fitness * 2.0)
        
        return self.fitness
    
    def clone(self) -> 'Brain':
        """Создаёт копию мозга."""
        new_genome = self.genome.clone()
        new_brain = Brain(new_genome, self.growth_rules)
        new_brain.gp = self.gp * 0.8  # Копия получает 80% GP (было 0.5)
        new_brain.fitness = self.fitness * 0.8  # Копия получает 80% фитнеса (не 0!)
        new_brain.age = self.age  # Копируем возраст
        return new_brain
    
    def mutate(self, mutation_rate: float = 0.1):
        """Применяет мутации к геному."""
        self.genome.mutate(mutation_rate)
        self.phenotype = Phenotype(self.genome)
    
    def __repr__(self):
        return f"Brain(nodes={self.phenotype.num_nodes}, gp={self.gp:.2f}, fitness={self.fitness:.3f})" 