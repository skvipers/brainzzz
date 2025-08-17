"""
Настройки для веб-приложения Brainzzz.
"""

import os
from pathlib import Path
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # WebSocket
    ws_ping_interval: int = 20
    ws_ping_timeout: int = 20
    
    # Ray
    ray_num_workers: int = 4
    ray_use_gpu: bool = False
    
    # Tasks
    default_population_size: int = 20
    default_mutation_rate: float = 0.3
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр настроек
settings = Settings()

# Пути
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True) 