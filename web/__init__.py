"""
Веб-интерфейс для инкубатора мозгов.

Модули:
- api: FastAPI веб-сервер с WebSocket поддержкой
- models: Pydantic модели данных
- websocket: WebSocket менеджер для real-time обновлений
"""

from .api import app, manager

__all__ = ['app', 'manager'] 