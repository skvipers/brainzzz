"""
Генетическая информация мозга.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
import random


@dataclass
class NodeGene:
    """Ген узла."""
    id: int
    node_type: str  # 'input', 'hidden', 'output', 'memory'
    activation_function: str  # 'sigmoid', 'tanh', 'relu', 'linear'
    bias: float = 0.0
    threshold: float = 0.5
    plasticity: float = 1.0  # Способность к изменению весов


@dataclass
class ConnectionGene:
    """Ген соединения."""
    id: int
    from_node: int
    to_node: int
    weight: float = 1.0
    enabled: bool = True
    plasticity: float = 1.0
    connection_type: str = 'excitatory'  # 'excitatory', 'inhibitory'


class Genome:
    """
    Генетическая информация, определяющая структуру и поведение мозга.
    
    Содержит:
    - Узлы (нейроны) с их параметрами
    - Соединения между узлами
    - Правила роста и развития
    """
    
    def __init__(self, 
                 input_size: int = 2,
                 output_size: int = 1,
                 hidden_size: int = 3):
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        
        # Гены
        self.node_genes: List[NodeGene] = []
        self.connection_genes: List[ConnectionGene] = []
        
        # Счётчики для генерации уникальных ID
        self.next_node_id = 0
        self.next_connection_id = 0
        
        # Инициализируем базовую структуру
        self._initialize_basic_structure()
    
    def _initialize_basic_structure(self):
        """Создаёт базовую структуру мозга."""
        # Входные узлы
        for i in range(self.input_size):
            self._add_node('input', 'linear')
        
        # Скрытые узлы
        for i in range(self.hidden_size):
            self._add_node('hidden', 'sigmoid')
        
        # Выходные узлы
        for i in range(self.output_size):
            self._add_node('output', 'sigmoid')
        
        # Соединения: входы -> скрытые -> выходы
        for input_id in range(self.input_size):
            for hidden_id in range(self.input_size, self.input_size + self.hidden_size):
                self._add_connection(input_id, hidden_id)
        
        for hidden_id in range(self.input_size, self.input_size + self.hidden_size):
            for output_id in range(self.input_size + self.hidden_size, 
                                 self.input_size + self.hidden_size + self.output_size):
                self._add_connection(hidden_id, output_id)
    
    def _add_node(self, node_type: str, activation_function: str) -> int:
        """Добавляет новый узел."""
        node_id = self.next_node_id
        self.next_node_id += 1
        
        node = NodeGene(
            id=node_id,
            node_type=node_type,
            activation_function=activation_function,
            bias=random.uniform(-0.5, 0.5),
            threshold=random.uniform(0.3, 0.7),
            plasticity=random.uniform(0.5, 1.5)
        )
        
        self.node_genes.append(node)
        return node_id
    
    def _add_connection(self, from_node: int, to_node: int) -> int:
        """Добавляет новое соединение."""
        connection_id = self.next_connection_id
        self.next_connection_id += 1
        
        connection = ConnectionGene(
            id=connection_id,
            from_node=from_node,
            to_node=to_node,
            weight=random.uniform(-2.0, 2.0),
            enabled=True,
            plasticity=random.uniform(0.5, 1.5),
            connection_type=random.choice(['excitatory', 'inhibitory'])
        )
        
        self.connection_genes.append(connection)
        return connection_id
    
    def add_node(self, node_type: str = 'hidden', 
                 activation_function: str = 'sigmoid') -> int:
        """
        Добавляет новый узел в геном.
        
        Args:
            node_type: Тип узла
            activation_function: Функция активации
            
        Returns:
            ID нового узла
        """
        return self._add_node(node_type, activation_function)
    
    def add_connection(self, from_node: int, to_node: int) -> int:
        """
        Добавляет новое соединение.
        
        Args:
            from_node: ID исходного узла
            to_node: ID целевого узла
            
        Returns:
            ID нового соединения
        """
        # Проверяем, что узлы существуют
        if not (self._node_exists(from_node) and self._node_exists(to_node)):
            raise ValueError(f"Узлы {from_node} или {to_node} не существуют")
        
        # Проверяем, что соединение не дублируется
        if self._connection_exists(from_node, to_node):
            raise ValueError(f"Соединение {from_node} -> {to_node} уже существует")
        
        return self._add_connection(from_node, to_node)
    
    def split_node(self, node_id: int) -> Tuple[int, int]:
        """
        Разделяет узел на два.
        
        Args:
            node_id: ID узла для разделения
            
        Returns:
            Tuple из ID двух новых узлов
        """
        if not self._node_exists(node_id):
            raise ValueError(f"Узел {node_id} не существует")
        
        # Создаём два новых узла
        new_node1_id = self._add_node('hidden', 'sigmoid')
        new_node2_id = self._add_node('hidden', 'sigmoid')
        
        # Перенаправляем входящие соединения на первый новый узел
        for conn in self.connection_genes:
            if conn.to_node == node_id:
                conn.to_node = new_node1_id
        
        # Перенаправляем исходящие соединения на второй новый узел
        for conn in self.connection_genes:
            if conn.from_node == node_id:
                conn.from_node = new_node2_id
        
        # Соединяем новые узлы
        self._add_connection(new_node1_id, new_node2_id)
        
        return new_node1_id, new_node2_id
    
    def _node_exists(self, node_id: int) -> bool:
        """Проверяет существование узла."""
        return any(node.id == node_id for node in self.node_genes)
    
    def _connection_exists(self, from_node: int, to_node: int) -> bool:
        """Проверяет существование соединения."""
        return any(conn.from_node == from_node and conn.to_node == to_node 
                  for conn in self.connection_genes)
    
    def mutate(self, mutation_rate: float = 0.1):
        """
        Применяет мутации к геному.
        
        Args:
            mutation_rate: Вероятность мутации каждого гена
        """
        # Мутации узлов
        for node in self.node_genes:
            if random.random() < mutation_rate:
                node.bias += random.uniform(-0.1, 0.1)
                node.threshold += random.uniform(-0.05, 0.05)
                node.plasticity += random.uniform(-0.1, 0.1)
        
        # Мутации соединений
        for conn in self.connection_genes:
            if random.random() < mutation_rate:
                conn.weight += random.uniform(-0.2, 0.2)
                conn.plasticity += random.uniform(-0.1, 0.1)
        
        # Случайные структурные мутации
        if random.random() < mutation_rate * 0.5:  # Увеличиваем вероятность структурных мутаций
            self._structural_mutation()
    
    def _structural_mutation(self):
        """Выполняет структурную мутацию."""
        mutation_type = random.choice(['add_node', 'add_connection', 'remove_connection'])
        
        if mutation_type == 'add_node' and len(self.node_genes) < 50:
            self.add_node()
        elif mutation_type == 'add_connection' and len(self.connection_genes) < 200:
            # Выбираем случайные узлы для соединения
            from_node = random.choice(self.node_genes).id
            to_node = random.choice(self.node_genes).id
            if from_node != to_node:
                try:
                    self.add_connection(from_node, to_node)
                except ValueError:
                    pass  # Игнорируем дубликаты
        elif mutation_type == 'remove_connection' and len(self.connection_genes) > 1:
            # Удаляем случайное соединение
            conn_to_remove = random.choice(self.connection_genes)
            self.connection_genes.remove(conn_to_remove)
    
    def clone(self) -> 'Genome':
        """Создаёт копию генома."""
        new_genome = Genome(self.input_size, self.output_size, self.hidden_size)
        new_genome.node_genes = [NodeGene(**vars(node)) for node in self.node_genes]
        new_genome.connection_genes = [ConnectionGene(**vars(conn)) for conn in self.connection_genes]
        new_genome.next_node_id = self.next_node_id
        new_genome.next_connection_id = self.next_connection_id
        return new_genome
    
    def get_node_by_id(self, node_id: int) -> NodeGene:
        """Возвращает узел по ID."""
        for node in self.node_genes:
            if node.id == node_id:
                return node
        raise ValueError(f"Узел {node_id} не найден")
    
    def get_connections_to(self, node_id: int) -> List[ConnectionGene]:
        """Возвращает все входящие соединения для узла."""
        return [conn for conn in self.connection_genes if conn.to_node == node_id]
    
    def get_connections_from(self, node_id: int) -> List[ConnectionGene]:
        """Возвращает все исходящие соединения для узла."""
        return [conn for conn in self.connection_genes if conn.from_node == node_id]
    
    def __repr__(self):
        return f"Genome(nodes={len(self.node_genes)}, connections={len(self.connection_genes)})" 