"""
Схемы WebSocket сообщений для Brainzzz API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Типы WebSocket сообщений."""

    POPULATION_UPDATE = "population_update"
    BRAIN_UPDATE = "brain_update"
    TASK_UPDATE = "task_update"
    EVOLUTION_STEP = "evolution_step"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


class BrainStats(BaseModel):
    """Статистика мозга."""

    id: str
    fitness: float
    nodes: int
    connections: int
    generation: int
    parent_ids: Optional[List[str]] = None


class PopulationStats(BaseModel):
    """Статистика популяции."""

    size: int
    avg_fitness: float
    max_fitness: float
    min_fitness: float
    avg_nodes: float
    avg_connections: float
    generation: int
    timestamp: datetime = Field(default_factory=datetime.now)


class TaskResult(BaseModel):
    """Результат выполнения задачи."""

    task_id: str
    task_name: str
    brain_id: str
    score: float
    completed: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class WebSocketMessage(BaseModel):
    """Базовое WebSocket сообщение."""

    type: MessageType
    schema_version: str = "1.0.0"  # Версия схемы
    ts: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any]


class PopulationUpdateMessage(WebSocketMessage):
    """Обновление популяции."""

    type: MessageType = MessageType.POPULATION_UPDATE
    data: PopulationStats


class BrainUpdateMessage(WebSocketMessage):
    """Обновление мозга."""

    type: MessageType = MessageType.BRAIN_UPDATE
    data: BrainStats


class TaskUpdateMessage(WebSocketMessage):
    """Обновление задачи."""

    type: MessageType = MessageType.TASK_UPDATE
    data: TaskResult


class EvolutionStepMessage(WebSocketMessage):
    """Шаг эволюции."""

    type: MessageType = MessageType.EVOLUTION_STEP
    data: Dict[str, Any]


class SystemStatusMessage(WebSocketMessage):
    """Статус системы."""

    type: MessageType = MessageType.SYSTEM_STATUS
    data: Dict[str, Any]


class ErrorMessage(WebSocketMessage):
    """Сообщение об ошибке."""

    type: MessageType = MessageType.ERROR
    data: Dict[str, Any]
