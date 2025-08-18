"""
Фенотипическое представление мозга.
"""

import numpy as np
from .genome import Genome


class Phenotype:
    """
    Фенотипическое представление мозга, созданное на основе генома.

    Содержит:
    - Матрицы весов и смещений
    - Функции активации
    - Методы для вычисления активаций
    """

    def __init__(self, genome: Genome):
        self.genome = genome
        self.num_nodes = len(genome.node_genes)

        # Создаём матрицы для быстрых вычислений
        self._build_matrices()

        # Кэш для функций активации
        self._activation_functions = {
            "sigmoid": self._sigmoid,
            "tanh": self._tanh,
            "relu": self._relu,
            "linear": self._linear,
        }

    def _build_matrices(self):
        """Строит матрицы для быстрых вычислений."""
        # Матрица весов (num_nodes x num_nodes)
        self.weight_matrix = np.zeros((self.num_nodes, self.num_nodes))

        # Вектор смещений
        self.bias_vector = np.zeros(self.num_nodes)

        # Вектор порогов
        self.threshold_vector = np.zeros(self.num_nodes)

        # Вектор пластичности
        self.plasticity_vector = np.zeros(self.num_nodes)

        # Матрица типов соединений (1 для возбуждающих, -1 для тормозных)
        self.connection_type_matrix = np.zeros((self.num_nodes, self.num_nodes))

        # Заполняем матрицы из генома
        for node in self.genome.node_genes:
            self.bias_vector[node.id] = node.bias
            self.threshold_vector[node.id] = node.threshold
            self.plasticity_vector[node.id] = node.plasticity

        for conn in self.genome.connection_genes:
            if conn.enabled:
                self.weight_matrix[conn.from_node, conn.to_node] = conn.weight
                self.connection_type_matrix[conn.from_node, conn.to_node] = (
                    1.0 if conn.connection_type == "excitatory" else -1.0
                )

    def compute_activations(self, current_activations: np.ndarray) -> np.ndarray:
        """
        Вычисляет новые активации на основе текущих.

        Args:
            current_activations: Текущие активации узлов

        Returns:
            Новые активации узлов
        """
        # Вычисляем взвешенную сумму входов
        weighted_inputs = np.dot(self.weight_matrix.T, current_activations)

        # Применяем смещения
        net_inputs = weighted_inputs + self.bias_vector

        # Применяем функции активации
        new_activations = np.zeros_like(current_activations)

        for i, node in enumerate(self.genome.node_genes):
            if node.node_type == "input":
                # Входные узлы сохраняют свои значения
                new_activations[i] = current_activations[i]
            else:
                # Применяем функцию активации
                activation_func = self._activation_functions.get(
                    node.activation_function, self._sigmoid
                )
                new_activations[i] = activation_func(net_inputs[i])

                # Применяем порог
                if new_activations[i] < node.threshold:
                    new_activations[i] = 0.0

        return new_activations

    def get_output_activations(self, activations: np.ndarray) -> np.ndarray:
        """
        Возвращает активации только выходных узлов.

        Args:
            activations: Активации всех узлов

        Returns:
            Активации выходных узлов
        """
        output_nodes = [
            i
            for i, node in enumerate(self.genome.node_genes)
            if node.node_type == "output"
        ]
        return activations[output_nodes]

    def get_input_nodes(self) -> list[int]:
        """Возвращает список ID входных узлов."""
        return [
            i
            for i, node in enumerate(self.genome.node_genes)
            if node.node_type == "input"
        ]

    def get_output_nodes(self) -> list[int]:
        """Возвращает список ID выходных узлов."""
        return [
            i
            for i, node in enumerate(self.genome.node_genes)
            if node.node_type == "output"
        ]

    def get_hidden_nodes(self) -> list[int]:
        """Возвращает список ID скрытых узлов."""
        return [
            i
            for i, node in enumerate(self.genome.node_genes)
            if node.node_type == "hidden"
        ]

    def get_memory_nodes(self) -> list[int]:
        """Возвращает список ID узлов памяти."""
        return [
            i
            for i, node in enumerate(self.genome.node_genes)
            if node.node_type == "memory"
        ]

    def get_node_connections(self, node_id: int) -> dict[str, list[int]]:
        """
        Возвращает все соединения для конкретного узла.

        Args:
            node_id: ID узла

        Returns:
            Словарь с входящими и исходящими соединениями
        """
        incoming = []
        outgoing = []

        for conn in self.genome.connection_genes:
            if conn.enabled:
                if conn.to_node == node_id:
                    incoming.append(conn.from_node)
                if conn.from_node == node_id:
                    outgoing.append(conn.to_node)

        return {"incoming": incoming, "outgoing": outgoing}

    def get_connection_strength(self, from_node: int, to_node: int) -> float:
        """
        Возвращает силу соединения между узлами.

        Args:
            from_node: ID исходного узла
            to_node: ID целевого узла

        Returns:
            Сила соединения (вес * тип)
        """
        weight = self.weight_matrix[from_node, to_node]
        conn_type = self.connection_type_matrix[from_node, to_node]
        return weight * conn_type

    def get_network_density(self) -> float:
        """
        Вычисляет плотность сети (отношение существующих соединений
        к максимально возможным).

        Returns:
            Плотность сети (0.0 - 1.0)
        """
        max_connections = self.num_nodes * (self.num_nodes - 1)
        actual_connections = sum(
            1 for conn in self.genome.connection_genes
            if conn.enabled
        )
        return actual_connections / max_connections if max_connections > 0 else 0.0

    def get_average_path_length(self) -> float:
        """
        Вычисляет среднюю длину пути между узлами.

        Returns:
            Средняя длина пути
        """
        # Простая реализация через матрицу достижимости
        reachability = self._compute_reachability_matrix()

        total_length = 0
        path_count = 0

        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if i != j and reachability[i, j] > 0:
                    total_length += reachability[i, j]
                    path_count += 1

        return total_length / path_count if path_count > 0 else 0.0

    def _compute_reachability_matrix(self) -> np.ndarray:
        """Вычисляет матрицу достижимости (минимальные расстояния между узлами)."""
        # Инициализируем матрицу расстояний
        distances = np.full((self.num_nodes, self.num_nodes), np.inf)
        np.fill_diagonal(distances, 0)

        # Заполняем прямые соединения
        for conn in self.genome.connection_genes:
            if conn.enabled:
                distances[conn.from_node, conn.to_node] = 1

        # Алгоритм Флойда-Уоршелла для кратчайших путей
        for k in range(self.num_nodes):
            for i in range(self.num_nodes):
                for j in range(self.num_nodes):
                    if distances[i, k] + distances[k, j] < distances[i, j]:
                        distances[i, j] = distances[i, k] + distances[k, j]

        # Заменяем inf на 0 для недостижимых узлов
        distances[distances == np.inf] = 0

        return distances

    # Функции активации
    def _sigmoid(self, x: float) -> float:
        """Сигмоидная функция активации."""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _tanh(self, x: float) -> float:
        """Гиперболический тангенс."""
        return np.tanh(x)

    def _relu(self, x: float) -> float:
        """ReLU функция активации."""
        return max(0.0, x)

    def _linear(self, x: float) -> float:
        """Линейная функция активации."""
        return x

    def update_weights(self, learning_rate: float = 0.01):
        """
        Обновляет веса соединений на основе пластичности.

        Args:
            learning_rate: Скорость обучения
        """
        for conn in self.genome.connection_genes:
            if conn.enabled and conn.plasticity > 0:
                # Простое правило Хебба: увеличиваем вес для часто
                # используемых соединений
                from_activation = np.random.random()  # Имитация активации
                to_activation = np.random.random()

                weight_change = (
                    learning_rate * conn.plasticity * from_activation * to_activation
                )
                conn.weight += weight_change

                # Ограничиваем веса
                conn.weight = np.clip(conn.weight, -5.0, 5.0)

        # Перестраиваем матрицы
        self._build_matrices()

    def __repr__(self):
        return (
            f"Phenotype(nodes={self.num_nodes}, "
            f"density={self.get_network_density():.3f}, "
            f"avg_path={self.get_average_path_length():.2f})"
        )
