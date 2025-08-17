"""
Модуль для эволюционных алгоритмов.

Содержит:
- EvolutionEngine: основной движок эволюции
- Selection: стратегии селекции
- Mutation: операторы мутации
- Crossover: операторы скрещивания
"""

from .evolution_engine import EvolutionEngine
from .selection import Selection
from .mutation import Mutation
from .crossover import Crossover

__all__ = ['EvolutionEngine', 'Selection', 'Mutation', 'Crossover'] 