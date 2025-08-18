"""
Модуль для работы с задачами и их оценкой.

Содержит:
- TaskManager: управление задачами
- BaseTask: базовый класс задачи
- XORTask: задача XOR
- SequenceTask: задача с последовательностями
"""

from .base_task import BaseTask
from .sequence_task import SequenceTask
from .task_manager import TaskManager
from .xor_task import XORTask

__all__ = ["TaskManager", "BaseTask", "XORTask", "SequenceTask"]
