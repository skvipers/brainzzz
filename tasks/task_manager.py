"""
Менеджер задач для управления и оценки выполнения задач.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .base_task import BaseTask
from brains import Brain


class TaskManager:
    """
    Управляет задачами и их оценкой.
    
    Функции:
    - Добавление/удаление задач
    - Оценка мозга на всех задачах
    - Анализ производительности
    - Генерация отчётов
    """
    
    def __init__(self):
        self.tasks: List[BaseTask] = []
        self.task_weights: Dict[str, float] = {}  # Веса задач для общей оценки
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def add_task(self, task: BaseTask, weight: float = 1.0):
        """
        Добавляет задачу в менеджер.
        
        Args:
            task: Задача для добавления
            weight: Вес задачи в общей оценке
        """
        self.tasks.append(task)
        self.task_weights[task.name] = weight
        
        # Нормализуем веса
        self._normalize_weights()
    
    def remove_task(self, task_name: str):
        """
        Удаляет задачу из менеджера.
        
        Args:
            task_name: Название задачи для удаления
        """
        self.tasks = [task for task in self.tasks if task.name != task_name]
        if task_name in self.task_weights:
            del self.task_weights[task_name]
        
        # Нормализуем веса
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Нормализует веса задач так, чтобы их сумма равнялась 1.0."""
        if not self.task_weights:
            return
        
        total_weight = sum(self.task_weights.values())
        if total_weight > 0:
            for task_name in self.task_weights:
                self.task_weights[task_name] /= total_weight
    
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
        
        results = []
        
        for task in self.tasks:
            try:
                # Генерируем тестовые данные
                test_data = task.generate_test_data()
                
                # Оцениваем решение
                score = task.evaluate_solution(brain, test_data)
                results.append(score)
                
            except Exception as e:
                # В случае ошибки даём нулевую оценку
                results.append(0.0)
        
        # Сохраняем историю оценок
        self._save_evaluation_history(brain, results)
        
        return results
    
    def get_overall_score(self, brain: Brain) -> float:
        """
        Вычисляет общую оценку мозга по всем задачам.
        
        Args:
            brain: Мозг для оценки
            
        Returns:
            Общая оценка (0.0 - 1.0)
        """
        if not self.tasks:
            return 0.0
        
        task_scores = self.evaluate_brain(brain)
        
        # Вычисляем взвешенную сумму
        overall_score = 0.0
        for i, task in enumerate(self.tasks):
            weight = self.task_weights.get(task.name, 1.0 / len(self.tasks))
            overall_score += weight * task_scores[i]
        
        return overall_score
    
    def _save_evaluation_history(self, brain: Brain, task_scores: List[float], overall_score: float = None):
        """Сохраняет историю оценок."""
        if overall_score is None:
            # Вычисляем overall_score локально, не вызывая get_overall_score
            overall_score = 0.0
            for i, task in enumerate(self.tasks):
                weight = self.task_weights.get(task.name, 1.0 / len(self.tasks))
                overall_score += weight * task_scores[i]
        
        history_entry = {
            'brain_id': id(brain),
            'brain_nodes': brain.phenotype.num_nodes,
            'brain_gp': brain.gp,
            'timestamp': np.datetime64('now'),
            'task_scores': dict(zip([task.name for task in self.tasks], task_scores)),
            'overall_score': overall_score
        }
        
        self.evaluation_history.append(history_entry)
        
        # Ограничиваем размер истории
        if len(self.evaluation_history) > 1000:
            self.evaluation_history = self.evaluation_history[-1000:]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику по задачам.
        
        Returns:
            Словарь со статистикой
        """
        if not self.tasks:
            return {}
        
        stats = {
            'total_tasks': len(self.tasks),
            'tasks': [],
            'average_difficulty': 0.0,
            'total_evaluations': len(self.evaluation_history)
        }
        
        total_difficulty = 0.0
        
        for task in self.tasks:
            task_info = task.get_task_info()
            task_info['weight'] = self.task_weights.get(task.name, 1.0 / len(self.tasks))
            stats['tasks'].append(task_info)
            
            total_difficulty += task.difficulty
        
        if self.tasks:
            stats['average_difficulty'] = total_difficulty / len(self.tasks)
        
        return stats
    
    def get_brain_performance_history(self, brain_id: int) -> List[Dict[str, Any]]:
        """
        Возвращает историю производительности конкретного мозга.
        
        Args:
            brain_id: ID мозга
            
        Returns:
            Список записей истории
        """
        return [entry for entry in self.evaluation_history if entry['brain_id'] == brain_id]
    
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
            'population_size': len(brains),
            'average_overall_score': np.mean([self.get_overall_score(brain) for brain in brains]),
            'best_overall_score': np.max([self.get_overall_score(brain) for brain in brains]),
            'worst_overall_score': np.min([self.get_overall_score(brain) for brain in brains]),
            'task_performance': {}
        }
        
        # Статистика по задачам
        for i, task in enumerate(self.tasks):
            task_scores = all_scores[:, i]
            stats['task_performance'][task.name] = {
                'average_score': float(np.mean(task_scores)),
                'best_score': float(np.max(task_scores)),
                'worst_score': float(np.min(task_scores)),
                'std_score': float(np.std(task_scores))
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
        return f"TaskManager(tasks={len(self.tasks)}, evaluations={len(self.evaluation_history)})" 