"""
Визуализация структуры мозга.
"""

from typing import Dict, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from brains import Brain


class BrainVisualizer:
    """
    Визуализирует структуру и активность мозга.

    Функции:
    - Граф узлов и соединений
    - Потоки активации
    - Анализ структуры
    """

    def __init__(self):
        self.colors = {
            "input": "#4CAF50",  # Зелёный
            "hidden": "#2196F3",  # Синий
            "output": "#FF9800",  # Оранжевый
            "memory": "#9C27B0",  # Фиолетовый
            "excitatory": "#4CAF50",  # Зелёный
            "inhibitory": "#F44336",  # Красный
        }

    def visualize_brain(
        self,
        brain: Brain,
        save_path: Optional[str] = None,
        show_activations: bool = True,
        show_weights: bool = True,
    ) -> plt.Figure:
        """
        Создаёт визуализацию мозга.

        Args:
            brain: Мозг для визуализации
            save_path: Путь для сохранения изображения
            show_activations: Показывать ли активации
            show_weights: Показывать ли веса соединений

        Returns:
            Фигура matplotlib
        """
        # Создаём граф
        G = self._create_network_graph(brain)

        # Создаём фигуру
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Граф структуры
        self._plot_structure_graph(G, brain, ax1, show_weights)

        # Граф активаций
        if show_activations:
            self._plot_activation_graph(G, brain, ax2)
        else:
            ax2.axis("off")

        # Заголовок
        fig.suptitle(
            f"Визуализация мозга\n"
            f"Узлы: {brain.phenotype.num_nodes}, "
            f"Соединения: {len(brain.genome.connection_genes)}, "
            f"Fitness: {brain.fitness:.3f}, "
            f"GP: {brain.gp:.2f}",
            fontsize=14,
        )

        plt.tight_layout()

        # Сохраняем, если указан путь
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Визуализация сохранена в {save_path}")

        return fig

    def _create_network_graph(self, brain: Brain) -> nx.DiGraph:
        """Создаёт NetworkX граф из мозга."""
        G = nx.DiGraph()

        # Добавляем узлы
        for node in brain.genome.node_genes:
            G.add_node(
                node.id,
                type=node.node_type,
                activation=node.activation_function,
                bias=node.bias,
                threshold=node.threshold,
            )

        # Добавляем соединения
        for conn in brain.genome.connection_genes:
            if conn.enabled:
                G.add_edge(
                    conn.from_node,
                    conn.to_node,
                    weight=conn.weight,
                    type=conn.connection_type,
                    plasticity=conn.plasticity,
                )

        return G

    def _plot_structure_graph(
        self, G: nx.DiGraph, brain: Brain, ax: plt.Axes, show_weights: bool
    ):
        """Рисует граф структуры."""
        # Позиции узлов
        pos = self._calculate_node_positions(brain)

        # Цвета узлов
        node_colors = [
            self.colors.get(G.nodes[node]["type"], "#757575") for node in G.nodes()
        ]

        # Размеры узлов
        node_sizes = [
            300 if G.nodes[node]["type"] in ["input", "output"] else 200
            for node in G.nodes()
        ]

        # Рисуем узлы
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes, ax=ax
        )

        # Рисуем рёбра
        if show_weights:
            # Цвета рёбер на основе весов
            edge_colors = []
            edge_widths = []
            for u, v, data in G.edges(data=True):
                weight = data["weight"]
                if data["type"] == "inhibitory":
                    edge_colors.append(self.colors["inhibitory"])
                else:
                    edge_colors.append(self.colors["excitatory"])
                edge_widths.append(abs(weight) * 2 + 0.5)
        else:
            edge_colors = [self.colors["excitatory"]] * len(G.edges())
            edge_widths = [1.0] * len(G.edges())

        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=edge_widths,
            arrows=True,
            arrowsize=15,
            ax=ax,
        )

        # Подписи узлов
        labels = {node: f"{node}\n{G.nodes[node]['type'][:3]}" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        ax.set_title("Структура мозга")
        ax.axis("off")

    def _plot_activation_graph(self, G: nx.DiGraph, brain: Brain, ax: plt.Axes):
        """Рисует граф активаций."""
        if not brain.history:
            ax.text(
                0.5,
                0.5,
                "Нет данных активации",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title("Активации")
            return

        # Берём последние активации
        activations = brain.history[-1]

        # Позиции узлов
        pos = self._calculate_node_positions(brain)

        # Цвета узлов на основе активаций
        node_colors = []
        for node in G.nodes():
            if node < len(activations):
                activation = activations[node]
                # Нормализуем активацию для цвета
                color_intensity = min(1.0, max(0.0, activation))
                node_colors.append(plt.cm.Reds(color_intensity))
            else:
                node_colors.append("#757575")

        # Размеры узлов на основе активаций
        node_sizes = []
        for node in G.nodes():
            if node < len(activations):
                activation = activations[node]
                size = 200 + activation * 300
                node_sizes.append(size)
            else:
                node_sizes.append(200)

        # Рисуем узлы
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes, ax=ax
        )

        # Рисуем рёбра
        edge_colors = []
        edge_widths = []
        for u, v, data in G.edges(data=True):
            if u < len(activations) and v < len(activations):
                # Интенсивность ребра на основе активаций
                intensity = (activations[u] + activations[v]) / 2
                edge_colors.append(plt.cm.Blues(intensity))
                edge_widths.append(intensity * 3 + 0.5)
            else:
                edge_colors.append("#CCCCCC")
                edge_widths.append(0.5)

        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=edge_widths,
            arrows=True,
            arrowsize=15,
            ax=ax,
        )

        # Подписи узлов
        labels = {
            node: (
                f"{node}\n{activations[node]:.2f}"
                if node < len(activations)
                else f"{node}\n0.00"
            )
            for node in G.nodes()
        }
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        ax.set_title("Активации узлов")
        ax.axis("off")

    def _calculate_node_positions(self, brain: Brain) -> Dict[int, np.ndarray]:
        """Вычисляет позиции узлов для визуализации."""
        pos = {}

        # Группируем узлы по типам
        input_nodes = brain.phenotype.get_input_nodes()
        hidden_nodes = brain.phenotype.get_hidden_nodes()
        output_nodes = brain.phenotype.get_output_nodes()
        memory_nodes = brain.phenotype.get_memory_nodes()

        # Позиционируем входные узлы слева
        for i, node_id in enumerate(input_nodes):
            pos[node_id] = np.array([0, 1 - i * 2 / max(1, len(input_nodes) - 1)])

        # Позиционируем скрытые узлы в центре
        for i, node_id in enumerate(hidden_nodes):
            pos[node_id] = np.array([0.5, 1 - i * 2 / max(1, len(hidden_nodes) - 1)])

        # Позиционируем выходные узлы справа
        for i, node_id in enumerate(output_nodes):
            pos[node_id] = np.array([1, 1 - i * 2 / max(1, len(output_nodes) - 1)])

        # Позиционируем узлы памяти внизу
        for i, node_id in enumerate(memory_nodes):
            pos[node_id] = np.array([0.5, -0.5 - i * 0.3])

        return pos

    def plot_thought_path(
        self, brain: Brain, save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Визуализирует путь мысли мозга.

        Args:
            brain: Мозг для анализа
            save_path: Путь для сохранения

        Returns:
            Фигура matplotlib
        """
        thought_path = brain.get_thought_path()

        if not thought_path:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(
                0.5,
                0.5,
                "Нет данных о пути мысли",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title("Путь мысли")
            return fig

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # График активаций по времени
        if brain.history:
            activations = np.array(brain.history)
            time_steps = range(len(activations))

            # Показываем активации для каждого узла
            for node_id in range(min(activations.shape[1], 10)):  # Первые 10 узлов
                ax1.plot(
                    time_steps,
                    activations[:, node_id],
                    label=f"Узел {node_id}",
                    alpha=0.7,
                )

            ax1.set_xlabel("Время")
            ax1.set_ylabel("Активация")
            ax1.set_title("Динамика активаций")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # Путь мысли
        ax2.plot(
            range(len(thought_path)), thought_path, "o-", linewidth=2, markersize=8
        )
        ax2.set_xlabel("Шаг")
        ax2.set_ylabel("ID узла")
        ax2.set_title("Путь мысли (последовательность активированных узлов)")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Путь мысли сохранён в {save_path}")

        return fig

    def __repr__(self):
        return "BrainVisualizer()"
