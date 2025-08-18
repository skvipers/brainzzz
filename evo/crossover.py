"""
Операторы скрещивания для эволюционного алгоритма.
"""

import secrets

from brains import Genome


class Crossover:
    """
    Управляет скрещиванием мозгов.

    Доступные типы скрещивания:
    - Uniform: равномерное скрещивание
    - SinglePoint: скрещивание в одной точке
    - TwoPoint: скрещивание в двух точках
    """

    def __init__(self, crossover_type: str = "uniform"):
        self.crossover_type = crossover_type

    def crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """
        Создаёт потомка путём скрещивания двух родителей.

        Args:
            parent1: Первый родитель
            parent2: Второй родитель

        Returns:
            Новый мозг-потомок
        """
        if self.crossover_type == "uniform":
            return self._uniform_crossover(parent1, parent2)
        elif self.crossover_type == "single_point":
            return self._single_point_crossover(parent1, parent2)
        elif self.crossover_type == "two_point":
            return self._two_point_crossover(parent1, parent2)
        else:
            return self._uniform_crossover(parent1, parent2)

    def _uniform_crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """Равномерное скрещивание."""
        # Клонируем первого родителя как основу
        offspring = parent1.clone()

        # Скрещиваем геномы
        offspring.genome = self._crossover_genomes(
            parent1.genome, parent2.genome, "uniform"
        )

        # Скрещиваем правила роста
        offspring.growth_rules = self._crossover_growth_rules(
            parent1.growth_rules, parent2.growth_rules
        )

        # Обновляем фенотип
        offspring.phenotype = offspring.phenotype.__class__(offspring.genome)

        return offspring

    def _single_point_crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """Скрещивание в одной точке."""
        offspring = parent1.clone()
        offspring.genome = self._crossover_genomes(
            parent1.genome, parent2.genome, "single_point"
        )
        offspring.growth_rules = self._crossover_growth_rules(
            parent1.growth_rules, parent2.growth_rules
        )
        offspring.phenotype = offspring.phenotype.__class__(offspring.genome)
        return offspring

    def _two_point_crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """Скрещивание в двух точках."""
        offspring = parent1.clone()
        offspring.genome = self._crossover_genomes(
            parent1.genome, parent2.genome, "two_point"
        )
        offspring.growth_rules = self._crossover_growth_rules(
            parent1.growth_rules, parent2.growth_rules
        )
        offspring.phenotype = offspring.phenotype.__class__(offspring.genome)
        return offspring

    def _crossover_genomes(self, genome1, genome2, method: str):
        """Скрещивает два генома."""
        # Создаём новый геном
        new_genome = genome1.clone()

        if method == "uniform":
            # Равномерное скрещивание: каждый ген с вероятностью 0.5
            # берётся от одного из родителей
            for i, node in enumerate(new_genome.node_genes):
                if secrets.randbelow(2) == 0:
                    parent2_node = (
                        genome2.node_genes[i] if i < len(genome2.node_genes) else node
                    )
                    node.bias = parent2_node.bias
                    node.threshold = parent2_node.threshold
                    node.plasticity = parent2_node.plasticity

            for i, conn in enumerate(new_genome.connection_genes):
                if secrets.randbelow(2) == 0:
                    parent2_conn = (
                        genome2.connection_genes[i]
                        if i < len(genome2.connection_genes)
                        else conn
                    )
                    conn.weight = parent2_conn.weight
                    conn.plasticity = parent2_conn.plasticity

        elif method == "single_point":
            # Скрещивание в одной точке
            crossover_point = secrets.randbelow(len(new_genome.node_genes) // 2)

            # Копируем гены после точки от второго родителя
            for i in range(crossover_point, len(new_genome.node_genes)):
                if i < len(genome2.node_genes):
                    parent2_node = genome2.node_genes[i]
                    new_genome.node_genes[i].bias = parent2_node.bias
                    new_genome.node_genes[i].threshold = parent2_node.threshold
                    new_genome.node_genes[i].plasticity = parent2_node.plasticity

        elif method == "two_point":
            # Скрещивание в двух точках
            point1 = secrets.randbelow(len(new_genome.node_genes) // 3)
            point2 = secrets.randbelow(
                2 * len(new_genome.node_genes) // 3, len(new_genome.node_genes)
            )

            # Копируем гены между точками от второго родителя
            for i in range(point1, point2):
                if i < len(genome2.node_genes):
                    parent2_node = genome2.node_genes[i]
                    new_genome.node_genes[i].bias = parent2_node.bias
                    new_genome.node_genes[i].threshold = parent2_node.threshold
                    new_genome.node_genes[i].plasticity = parent2_node.plasticity

        return new_genome

    def _crossover_growth_rules(self, rules1, rules2):
        """Скрещивает правила роста."""
        # Создаём новые правила роста
        new_rules = rules1.clone()

        # Скрещиваем параметры
        if secrets.randbelow(2) == 0:
            new_rules.growth_probability = rules2.growth_probability
        if secrets.randbelow(2) == 0:
            new_rules.complexity_penalty = rules2.complexity_penalty
        if secrets.randbelow(2) == 0:
            new_rules.max_nodes = rules2.max_nodes
        if secrets.randbelow(2) == 0:
            new_rules.max_connections = rules2.max_connections

        return new_rules

    def set_crossover_type(self, crossover_type: str):
        """Устанавливает тип скрещивания."""
        if crossover_type in ["uniform", "single_point", "two_point"]:
            self.crossover_type = crossover_type
        else:
            raise ValueError("Неизвестный тип скрещивания")

    def __repr__(self):
        return f"Crossover(type={self.crossover_type})"
