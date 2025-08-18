"""
Модуль для работы с задачами и их оценкой.

Содержит:
- TaskManager: управление задачами
- BaseTask: базовый класс задачи
- XORTask: задача XOR
- SequenceTask: задача с последовательностями
"""

from .task_manager import TaskManager
from .base_task import BaseTask
from .xor_task import XORTask
from .sequence_task import SequenceTask

__all__ = ["TaskManager", "BaseTask", "XORTask", "SequenceTask"]
