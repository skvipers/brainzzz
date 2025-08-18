"""
Задача с последовательностями для тестирования памяти и паттернов.
"""

import numpy as np
from typing import List, Tuple
from .base_task import BaseTask
from brains import Brain


class SequenceTask(BaseTask):
    """
    Задача с последовательностями.

    Тестирует способность мозга запоминать и воспроизводить паттерны.
    Более сложная задача, требующая памяти.
    """

    def __init__(self, sequence_length: int = 3):
        super().__init__(name="Sequence", difficulty=0.6)
        self.sequence_length = sequence_length
        self.description = (
            f"Задача с последовательностями длиной {sequence_length}: "
            f"запомнить и воспроизвести паттерн"
        )
        self.input_size = sequence_length
        self.output_size = sequence_length

        # Генерируем фиксированные тестовые данные
        self._test_data = self._generate_sequence_data()

    def _generate_sequence_data(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Генерирует данные для задачи с последовательностями.

        Returns:
            Список пар (вход, ожидаемый_выход)
        """
        test_sequences = []

        # Простые повторяющиеся паттерны
        patterns = [
            ([0.0, 1.0, 0.0], [0.0, 1.0, 0.0]),  # 010 -> 010
            ([1.0, 0.0, 1.0], [1.0, 0.0, 1.0]),  # 101 -> 101
            ([0.0, 0.0, 1.0], [0.0, 0.0, 1.0]),  # 001 -> 001
            ([1.0, 1.0, 0.0], [1.0, 1.0, 0.0]),  # 110 -> 110
        ]

        for input_seq, output_seq in patterns:
            test_sequences.append((np.array(input_seq), np.array(output_seq)))

        # Добавляем случайные последовательности
        np.random.seed(42)  # Для воспроизводимости
        for _ in range(6):
            input_seq = np.random.choice([0.0, 1.0], size=self.sequence_length)
            output_seq = input_seq.copy()  # Идеальный ответ - повторить вход
            test_sequences.append((input_seq, output_seq))

        return test_sequences

    def generate_test_data(
        self, num_samples: int = 100
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Генерирует тестовые данные для задачи.

        Args:
            num_samples: Количество тестовых примеров (игнорируется)

        Returns:
            Список пар (вход, ожидаемый_выход)
        """
        return self._test_data

    def evaluate_solution(
        self, brain: Brain, test_data: List[Tuple[np.ndarray, np.ndarray]]
    ) -> float:
        """
        Оценивает решение задачи с последовательностями мозгом.

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

                # Проверяем размер выхода
                if len(brain_output) >= self.sequence_length:
                    # Вычисляем ошибку для каждого элемента последовательности
                    sequence_error = 0.0
                    for i in range(self.sequence_length):
                        predicted = brain_output[i]
                        expected = expected_output[i]

                        # Квадратичная ошибка
                        element_error = (predicted - expected) ** 2
                        sequence_error += element_error

                    # Нормализуем ошибку по длине последовательности
                    avg_sequence_error = sequence_error / self.sequence_length
                    total_error += avg_sequence_error

                else:
                    # Штраф за неправильный размер выхода
                    total_error += 1.0

            except Exception:
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
        info.update(
            {
                "type": "sequence_memory",
                "input_range": "[0, 1]",
                "output_range": "[0, 1]",
                "sequence_length": self.sequence_length,
                "test_cases": len(self._test_data),
                "requires_memory": True,
            }
        )
        return info

    def __repr__(self):
        return (
            f"SequenceTask(difficulty={self.difficulty:.2f}, "
            f"length={self.sequence_length}, "
            f"test_cases={len(self._test_data)})"
        )
