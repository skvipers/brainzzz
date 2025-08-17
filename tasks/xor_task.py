"""
Задача XOR для тестирования способности к нелинейной классификации.
"""

import numpy as np
from typing import List, Tuple
from .base_task import BaseTask
from brains import Brain


class XORTask(BaseTask):
    """
    Задача XOR (исключающее ИЛИ).
    
    Тестирует способность мозга решать нелинейно разделимые задачи.
    Простая задача для базового тестирования.
    """
    
    def __init__(self):
        super().__init__(
            name="XOR",
            difficulty=0.3
        )
        self.description = "Задача XOR: классифицировать входные данные по правилу исключающего ИЛИ"
        self.input_size = 2
        self.output_size = 1
        
        # Генерируем фиксированные тестовые данные
        self._test_data = self._generate_xor_data()
    
    def _generate_xor_data(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Генерирует данные для задачи XOR.
        
        Returns:
            Список пар (вход, ожидаемый_выход)
        """
        # XOR таблица истинности
        inputs = [
            np.array([0.0, 0.0]),  # 0 XOR 0 = 0
            np.array([0.0, 1.0]),  # 0 XOR 1 = 1
            np.array([1.0, 0.0]),  # 1 XOR 0 = 1
            np.array([1.0, 1.0])   # 1 XOR 1 = 0
        ]
        
        outputs = [
            np.array([0.0]),  # 0
            np.array([1.0]),  # 1
            np.array([1.0]),  # 1
            np.array([0.0])   # 0
        ]
        
        return list(zip(inputs, outputs))
    
    def generate_test_data(self, num_samples: int = 100) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Генерирует тестовые данные для задачи.
        
        Args:
            num_samples: Количество тестовых примеров (игнорируется для XOR)
            
        Returns:
            Список пар (вход, ожидаемый_выход)
        """
        return self._test_data
    
    def evaluate_solution(self, brain: Brain, test_data: List[Tuple[np.ndarray, np.ndarray]]) -> float:
        """
        Оценивает решение задачи XOR мозгом.
        
        Args:
            brain: Мозг для тестирования
            test_data: Тестовые данные
            
        Returns:
            Оценка решения (0.0 - 1.0)
        """
        if not test_data:
            return 0.0
        
        total_error = 0.0
        num_tests = len(test_data)
        
        for input_data, expected_output in test_data:
            try:
                # Получаем выход мозга
                brain_output = brain.process_input(input_data)
                
                # Вычисляем ошибку
                if len(brain_output) >= 1:
                    predicted = brain_output[0]
                    expected = expected_output[0]
                    
                    # Квадратичная ошибка
                    error = (predicted - expected) ** 2
                    total_error += error
                else:
                    # Штраф за неправильный размер выхода
                    total_error += 1.0
                    
            except Exception as e:
                # Штраф за ошибки выполнения
                total_error += 1.0
        
        # Нормализуем ошибку
        avg_error = total_error / num_tests
        
        # Преобразуем ошибку в оценку (0.0 - 1.0)
        # 0 ошибка = 1.0, максимальная ошибка = 0.0
        score = max(0.0, 1.0 - avg_error)
        
        return score
    
    def get_task_info(self) -> dict:
        """Возвращает расширенную информацию о задаче."""
        info = super().get_task_info()
        info.update({
            'type': 'classification',
            'input_range': '[0, 1]',
            'output_range': '[0, 1]',
            'test_cases': len(self._test_data),
            'nonlinear': True
        })
        return info
    
    def __repr__(self):
        return f"XORTask(difficulty={self.difficulty:.2f}, test_cases={len(self._test_data)})" 