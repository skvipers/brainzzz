"""
Операторы мутации для эволюционного алгоритма.
"""

import random
from brains import Brain


class Mutation:
    """
    Управляет мутациями мозгов.

    Доступные типы мутаций:
    - Genome: мутация генома
    - Growth: мутация правил роста
    - Structural: структурные мутации
    """

    def __init__(self, mutation_strength: float = 0.1):
        self.mutation_strength = mutation_strength

    def mutate(self, brain: Brain):
        """
        Применяет мутации к мозгу.

        Args:
            brain: Мозг для мутации
        """
        # Мутация генома
        self._mutate_genome(brain)

        # Мутация правил роста
        self._mutate_growth_rules(brain)

        # Структурные мутации
        self._structural_mutation(brain)

    def _mutate_genome(self, brain: Brain):
        """Мутирует геном мозга."""
        # Применяем мутации к геному
        brain.genome.mutate(self.mutation_strength)

        # Обновляем фенотип
        brain.phenotype = brain.phenotype.__class__(brain.genome)

    def _mutate_growth_rules(self, brain: Brain):
        """Мутирует правила роста."""
        growth_rules = brain.growth_rules

        # Мутируем параметры роста
        if random.random() < self.mutation_strength:
            growth_rules.growth_probability += random.uniform(-0.05, 0.05)
            growth_rules.growth_probability = max(
                0.01, min(0.5, growth_rules.growth_probability)
            )

        if random.random() < self.mutation_strength:
            growth_rules.complexity_penalty += random.uniform(-0.005, 0.005)
            growth_rules.complexity_penalty = max(
                0.001, min(0.1, growth_rules.complexity_penalty)
            )

    def _structural_mutation(self, brain: Brain):
        """Применяет структурные мутации."""
        if random.random() < self.mutation_strength * 0.1:
            # Случайно добавляем узел
            if brain.phenotype.num_nodes < brain.growth_rules.max_nodes:
                brain.genome.add_node()
                brain.phenotype = brain.phenotype.__class__(brain.genome)

        if random.random() < self.mutation_strength * 0.1:
            # Случайно добавляем соединение
            if len(brain.genome.connection_genes) < brain.growth_rules.max_connections:
                # Выбираем случайные узлы
                nodes = [node.id for node in brain.genome.node_genes]
                if len(nodes) >= 2:
                    from_node = random.choice(nodes)
                    to_node = random.choice(nodes)
                    if from_node != to_node:
                        try:
                            brain.genome.add_connection(from_node, to_node)
                            brain.phenotype = brain.phenotype.__class__(brain.genome)
                        except ValueError:
                            pass  # Игнорируем дубликаты

    def set_mutation_strength(self, strength: float):
        """Устанавливает силу мутации."""
        if 0.0 <= strength <= 1.0:
            self.mutation_strength = strength
        else:
            raise ValueError("Сила мутации должна быть в диапазоне [0.0, 1.0]")

    def __repr__(self):
        return f"Mutation(strength={self.mutation_strength:.3f})"
