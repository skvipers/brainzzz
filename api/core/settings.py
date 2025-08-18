"""
Настройки для API Brainzzz.
"""

from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки API приложения."""

    # Redis (Event Bus)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_channel: str = "brainzzz.events"

    # WebSocket
    ws_ping_interval: int = 20
    ws_ping_timeout: int = 20
    ws_max_connections: int = 100  # Нормальное значение для продакшена
    ws_connection_timeout: int = 30

    # API
    api_host: str = "127.0.0.1"  # Безопасный localhost вместо 0.0.0.0
    api_port: int = 8000  # Стандартный порт для API
    api_debug: bool = False

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    log_level: str = "INFO"

    # Пути (будут установлены после создания экземпляра)
    DATA_DIR: Optional[Path] = None
    LOGS_DIR: Optional[Path] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр настроек
settings = Settings()

# Пути
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Добавляем пути в настройки
settings.DATA_DIR = DATA_DIR
settings.LOGS_DIR = LOGS_DIR
