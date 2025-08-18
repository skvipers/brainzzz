"""
Менеджер задач для оценки мозгов.
"""

import logging
from typing import Any, Dict, List

import numpy as np

from brains import Brain

from .base_task import BaseTask

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Управляет задачами для оценки мозгов.

    Функции:
    - Регистрация задач
    - Оценка мозгов на задачах
    - Анализ производительности
    - Рекомендации по задачам
    """

    def __init__(self):
        self.tasks: List[BaseTask] = []
        self.task_weights: Dict[str, float] = {}
        self.evaluation_history: List[Dict[str, Any]] = []

    def add_task(self, task: BaseTask, weight: float = 1.0):
        """
        Добавляет задачу в менеджер.

        Args:
            task: Задача для добавления
            weight: Вес задачи в общей оценке
        """
        if task.name in [t.name for t in self.tasks]:
            logger.warning(f"Задача {task.name} уже существует, заменяем")
            self.remove_task(task.name)

        self.tasks.append(task)
        self.task_weights[task.name] = weight
        logger.info(f"Добавлена задача: {task.name} (вес: {weight})")

    def remove_task(self, task_name: str):
        """
        Удаляет задачу из менеджера.

        Args:
            task_name: Имя задачи для удаления
        """
        self.tasks = [t for t in self.tasks if t.name != task_name]
        if task_name in self.task_weights:
            del self.task_weights[task_name]
        logger.info(f"Удалена задача: {task_name}")

    def evaluate_brain(self, brain: Brain) -> List[float]:
        """
        Оценивает мозг на всех задачах.

        Args:
            brain: Мозг для оценки

        Returns:
            Список оценок по каждой задаче
        """
        if not self.tasks:
            return []

        scores = []
        for task in self.tasks:
            try:
                # Генерируем тестовые данные для задачи
                test_data = task.generate_test_data(num_samples=10)
                # Оцениваем решение
                score = task.evaluate_solution(brain, test_data)
                scores.append(score)
            except Exception as e:
                logger.error(f"Ошибка оценки задачи {task.name}: {e}")
                scores.append(0.0)

        # Сохраняем результат в истории
        self.evaluation_history.append(
            {
                "brain_id": id(brain),
                "task_scores": scores,
                "overall_score": self.get_overall_score(brain),
                "timestamp": "2025-01-18T00:00:00Z",
            }
        )

        return scores

    def get_overall_score(self, brain: Brain) -> float:
        """
        Вычисляет общую оценку мозга.

        Args:
            brain: Мозг для оценки

        Returns:
            Общая оценка
        """
        if not self.tasks:
            return 0.0

        task_scores = self.evaluate_brain(brain)
        if not task_scores:
            return 0.0

        # Взвешенное среднее по задачам
        total_weight = sum(self.task_weights.get(task.name, 1.0) for task in self.tasks)
        if total_weight == 0:
            return np.mean(task_scores)

        weighted_sum = sum(
            score * self.task_weights.get(task.name, 1.0)
            for score, task in zip(task_scores, self.tasks)
        )

        return weighted_sum / total_weight

    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику по задачам.

        Returns:
            Словарь со статистикой
        """
        if not self.tasks:
            return {}

        stats = {"total_tasks": len(self.tasks), "tasks": [], "average_difficulty": 0.0}

        total_difficulty = 0.0

        for task in self.tasks:
            task_info = task.get_task_info()
            task_info["weight"] = self.task_weights.get(
                task.name, 1.0 / len(self.tasks)
            )
            stats["tasks"].append(task_info)

            total_difficulty += task.difficulty

        if self.tasks:
            stats["average_difficulty"] = total_difficulty / len(self.tasks)

        return stats

    def get_brain_performance_history(self, brain_id: int) -> List[Dict[str, Any]]:
        """
        Возвращает историю производительности конкретного мозга.

        Args:
            brain_id: ID мозга

        Returns:
            Список записей истории
        """
        return [
            entry for entry in self.evaluation_history if entry["brain_id"] == brain_id
        ]

    def get_population_statistics(self, brains: List[Brain]) -> Dict[str, Any]:
        """
        Возвращает статистику популяции мозгов.

        Args:
            brains: Список мозгов

        Returns:
            Словарь со статистикой популяции
        """
        if not brains:
            return {}

        # Оцениваем всех мозгов
        all_scores = []
        for brain in brains:
            scores = self.evaluate_brain(brain)
            all_scores.append(scores)

        all_scores = np.array(all_scores)

        stats = {
            "population_size": len(brains),
            "average_overall_score": np.mean(
                [self.get_overall_score(brain) for brain in brains]
            ),
            "best_overall_score": np.max(
                [self.get_overall_score(brain) for brain in brains]
            ),
            "worst_overall_score": np.min(
                [self.get_overall_score(brain) for brain in brains]
            ),
            "task_performance": {},
        }

        # Статистика по задачам
        for i, task in enumerate(self.tasks):
            task_scores = all_scores[:, i]
            stats["task_performance"][task.name] = {
                "average_score": float(np.mean(task_scores)),
                "best_score": float(np.max(task_scores)),
                "worst_score": float(np.min(task_scores)),
                "std_score": float(np.std(task_scores)),
            }

        return stats

    def get_recommended_tasks(self, brain: Brain) -> List[BaseTask]:
        """
        Возвращает список задач, рекомендованных для мозга.

        Args:
            brain: Мозг для анализа

        Returns:
            Список рекомендованных задач
        """
        if not self.tasks:
            return []

        # Оцениваем мозг на всех задачах
        task_scores = self.evaluate_brain(brain)

        # Сортируем задачи по сложности и производительности
        task_analysis = []
        for i, task in enumerate(self.tasks):
            score = task_scores[i]
            difficulty = task.difficulty

            # Рекомендуем задачи, которые мозг может решить, но с трудом
            recommendation_score = score * (1.0 - score) * difficulty

            task_analysis.append((task, recommendation_score))

        # Сортируем по убыванию рекомендации
        task_analysis.sort(key=lambda x: x[1], reverse=True)

        return [task for task, _ in task_analysis]

    def __repr__(self):
        return (
            f"TaskManager(tasks={len(self.tasks)}, "
            f"evaluations={len(self.evaluation_history)})"
        )
