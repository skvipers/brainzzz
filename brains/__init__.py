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
from .phenotype import Phenotype
from .growth_rules import GrowthRules

__all__ = ["Brain", "Genome", "Phenotype", "GrowthRules"]
