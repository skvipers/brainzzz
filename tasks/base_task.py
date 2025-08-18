"""
Базовый класс для задач.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Dict
from brains import Brain


class BaseTask(ABC):
    """
    Абстрактный базовый класс для всех задач.

    Каждая задача должна реализовывать:
    - Генерацию тестовых данных
    - Оценку результатов
    - Метрики сложности
    """

    def __init__(self, name: str, difficulty: float = 1.0):
        self.name = name
        self.difficulty = difficulty  # 0.0 - 1.0
        self.description = ""
        self.input_size = 0
        self.output_size = 0

    @abstractmethod
    def generate_test_data(
        self, num_samples: int = 100
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Генерирует тестовые данные для задачи.

        Args:
            num_samples: Количество тестовых примеров

        Returns:
            Список пар (вход, ожидаемый_выход)
        """
        pass

    @abstractmethod
    def evaluate_solution(
        self, brain: Brain, test_data: List[Tuple[np.ndarray, np.ndarray]]
    ) -> float:
        """
        Оценивает решение задачи мозгом.

        Args:
            brain: Мозг для тестирования
            test_data: Тестовые данные

        Returns:
            Оценка решения (0.0 - 1.0)
        """
        pass

    def get_complexity_score(self) -> float:
        """
        Возвращает оценку сложности задачи.

        Returns:
            Оценка сложности (0.0 - 1.0)
        """
        return self.difficulty

    def get_task_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о задаче.

        Returns:
            Словарь с информацией о задаче
        """
        return {
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "input_size": self.input_size,
            "output_size": self.output_size,
            "complexity_score": self.get_complexity_score(),
        }

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.name}, "
            f"difficulty={self.difficulty:.2f})"
        )
