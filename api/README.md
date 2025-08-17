# 🧠 Brainzzz API

API модуль для Brainzzz - шлюз между runner и web фронтендом.

## Архитектура

API следует принципам архитектуры Brainzzz:

- **НЕ импортирует** модули из `runner` (brains, dist, tasks)
- Общается с runner только через **Redis события** и **файлы снапшотов**
- Предоставляет **WebSocket** для real-time коммуникации
- Предоставляет **REST API** для управления симуляцией

## Структура

```
api/
├── core/           # Схемы, настройки, адаптеры
├── ws/            # WebSocket хаб
├── rest/          # REST endpoints
├── events/        # Publisher/validator событий
├── tasks/         # Управляющие эндпоинты
├── main.py        # FastAPI app
└── requirements.txt
```

## Запуск

```bash
cd api
pip install -r requirements.txt
python main.py
```

Или через uvicorn:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### WebSocket
- `/ws` - Real-time события

### REST API
- `GET /api/v1/health` - Проверка здоровья
- `GET /api/v1/status` - Статус системы
- `GET /api/v1/population/stats` - Статистика популяции
- `GET /api/v1/brains/{id}/stats` - Статистика мозга
- `POST /api/v1/control/pause` - Пауза симуляции
- `POST /api/v1/control/resume` - Возобновление
- `POST /api/v1/control/snapshot` - Создание снапшота
- `GET /api/v1/snapshots` - Список снапшотов

## Конфигурация

Через `.env` файл:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

## WebSocket сообщения

Все сообщения имеют формат:

```json
{
  "type": "population_update",
  "schema": "1.0.0",
  "ts": "2025-01-18T00:00:00Z",
  "data": { ... }
}
```

## События Redis

API слушает канал `brainzzz.events` для получения событий от runner:

- `population_update` - Обновление популяции
- `brain_update` - Обновление мозга
- `task_update` - Результат задачи
- `evolution_step` - Шаг эволюции
- `control` - Команды управления 