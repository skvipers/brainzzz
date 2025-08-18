"""
Модуль для эволюционных алгоритмов.

Содержит:
- EvolutionEngine: основной движок эволюции
- Selection: стратегии селекции
- Mutation: операторы мутации
- Crossover: операторы скрещивания
"""

from .crossover import Crossover
from .evolution_engine import EvolutionEngine
from .mutation import Mutation
from .selection import Selection

__all__ = ["EvolutionEngine", "Selection", "Mutation", "Crossover"]
