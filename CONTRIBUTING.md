# 🤝 Руководство по вкладу в проект

Спасибо, что решили внести свой вклад в проект Brainzzz! 🧠

## 📋 Содержание

- [Как внести вклад](#как-внести-вклад)
- [Стиль кода](#стиль-кода)
- [Тестирование](#тестирование)
- [Pull Request процесс](#pull-request-процесс)
- [Сообщения коммитов](#сообщения-коммитов)

## 🚀 Как внести вклад

### 1. Fork и Clone

```bash
# Fork репозитория на GitHub
# Затем clone вашего fork
git clone https://github.com/YOUR_USERNAME/brainzzz.git
cd brainzzz

# Добавьте upstream remote
git remote add upstream https://github.com/skvipers/brainzzz.git
```

### 2. Создайте feature branch

```bash
git checkout -b feature/amazing-feature
# или
git checkout -b fix/bug-description
```

### 3. Внесите изменения

- Следуйте [стилю кода](#стиль-кода)
- Добавьте тесты для новых функций
- Обновите документацию при необходимости

### 4. Commit и Push

```bash
git add .
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature
```

### 5. Создайте Pull Request

- Перейдите на GitHub
- Создайте Pull Request из вашего fork
- Заполните шаблон PR
- Дождитесь review

## 📝 Стиль кода

### Python

- **Форматирование**: Black (длина строки 88 символов)
- **Импорты**: isort для сортировки
- **Линтинг**: flake8
- **Типизация**: mypy (где возможно)

```bash
# Автоматическое форматирование
black brains/ evo/ tasks/ api/
isort brains/ evo/ tasks/ api/
```

### TypeScript/React

- **Форматирование**: Prettier
- **Линтинг**: ESLint
- **Компоненты**: функциональные с хуками
- **Типизация**: строгая TypeScript

### Общие принципы

- Читаемый и понятный код
- Комментарии на английском языке
- Следуйте принципам SOLID
- DRY (Don't Repeat Yourself)

## 🧪 Тестирование

### Backend тесты

```bash
# Установка зависимостей для тестов
pip install pytest pytest-cov pytest-mock

# Запуск тестов
pytest tests/ -v --cov=brains --cov=evo --cov=tasks

# С coverage отчетом
pytest tests/ --cov=brains --cov-report=html
```

### Frontend тесты

```bash
cd web/frontend
npm test
npm run test:coverage
```

### Требования к тестам

- Покрытие кода > 80%
- Тесты для всех новых функций
- Mock внешних зависимостей
- Тестирование edge cases

## 🔄 Pull Request процесс

### 1. Подготовка PR

- Убедитесь, что все тесты проходят
- Обновите документацию при необходимости
- Проверьте, что код соответствует стилю

### 2. Шаблон PR

```markdown
## Описание
Краткое описание изменений

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование
- [ ] Backend тесты проходят
- [ ] Frontend тесты проходят
- [ ] Ручное тестирование выполнено

## Checklist
- [ ] Код соответствует стилю проекта
- [ ] Добавлены тесты для новых функций
- [ ] Обновлена документация
- [ ] PR готов к review
```

### 3. Review процесс

- Code review обязателен
- CI/CD проверки должны пройти
- Address feedback от reviewers
- Squash commits при необходимости

## 💬 Сообщения коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new brain visualization component
fix: resolve memory leak in evolution engine
docs: update API documentation
test: add unit tests for crossover module
refactor: simplify brain growth algorithm
style: format code with black
perf: optimize population evaluation
chore: update dependencies
```

### Типы коммитов

- `feat`: новая функция
- `fix`: исправление бага
- `docs`: документация
- `style`: форматирование
- `refactor`: рефакторинг
- `test`: тесты
- `chore`: обслуживание

## 🏷️ Labels и Milestones

### Labels

- `bug`: ошибки
- `enhancement`: улучшения
- `documentation`: документация
- `good first issue`: для новичков
- `help wanted`: нужна помощь
- `priority: high/medium/low`

### Milestones

- `v1.0.0`: первая стабильная версия
- `v1.1.0`: улучшения и исправления
- `v2.0.0`: мажорные изменения

## 📞 Получение помощи

- **Issues**: создавайте issue для багов и feature requests
- **Discussions**: используйте GitHub Discussions для вопросов
- **Email**: skvipers@gmail.com

## 🙏 Благодарности

Спасибо всем участникам проекта! Ваш вклад делает Brainzzz лучше с каждым днем.

---

**Помните**: Каждый PR, даже самый маленький, важен для проекта! 🚀 