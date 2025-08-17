"""
Модуль для визуализации мозгов и эволюции.

Содержит:
- BrainVisualizer: визуализация структуры мозга
- EvolutionVisualizer: визуализация процесса эволюции
- WebServer: веб-интерфейс для интерактивной визуализации
"""

from .brain_visualizer import BrainVisualizer
from .evolution_visualizer import EvolutionVisualizer
from .web_server import WebServer
from ..web.api import app as web_app

__all__ = ['BrainVisualizer', 'EvolutionVisualizer', 'WebServer'] 