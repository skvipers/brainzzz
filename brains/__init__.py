"""
Модуль для работы с когнитивными структурами (мозгами).

Содержит:
- Brain: основной класс мозга
- Genome: генетическая информация
- Phenotype: фенотипическое представление
- GrowthRules: правила роста и развития
"""

from .brain import Brain
from .genome import Genome
from .growth_rules import GrowthRules
from .phenotype import Phenotype

__all__ = ["Brain", "Genome", "Phenotype", "GrowthRules"]
