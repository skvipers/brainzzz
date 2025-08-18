"""
Настройки для веб-приложения Brainzzz.
"""

import os
from pathlib import Path

# Пути
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# WebSocket URL (берем из env или используем по умолчанию)
WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws")

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")
