# Habit Tracker API

Backend-приложение для отслеживания полезных привычек с автоматическими напоминаниями через Telegram.

Проект разработан на Django и Django REST Framework. Пользователи могут создавать, просматривать, редактировать и удалять собственные привычки, просматривать публичные привычки других пользователей и получать напоминания по расписанию.

## Технологии

- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- PostgreSQL не требуется — используется SQLite
- Celery и Redis
- Telegram Bot API
- drf-spectacular (Swagger/OpenAPI)
- django-cors-headers
- Poetry
- Pytest, pytest-django, pytest-cov
- Ruff

## Функциональность

- Регистрация пользователей и JWT-аутентификация.
- CRUD-операции с привычками.
- Ограничение доступа к привычкам их владельцем.
- Публичный список привычек с доступом без авторизации.
- Пагинация по пять записей по умолчанию.
- Валидация продолжительности, периодичности, вознаграждений и связанных приятных привычек.
- Автоматические Telegram-напоминания через Celery.
- Привязка Telegram chat ID к авторизованному пользователю.
- Документация API через Swagger.

## Установка и запуск

### 1. Требования

Для запуска необходимы Python 3.12, Poetry, Redis и Git. Для Redis можно использовать Docker Desktop.

### 2. Установка зависимостей

Клонировать репозиторий и перейти в папку проекта:

```bash
git clone <repository-url>
cd project_5
```

Установить зависимости:

```bash
poetry install
```

### 3. Настройка переменных окружения

Создать `.env` на основе `.env.template`.

Для Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

Пример содержимого `.env`:

```dotenv
SECRET_KEY=replace-with-a-secure-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
TIME_ZONE=Europe/Athens
CORS_ALLOWED_ORIGINS=http://localhost:3000

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

TELEGRAM_BOT_TOKEN=replace-with-your-bot-token
```

Заменить `SECRET_KEY` и `TELEGRAM_BOT_TOKEN` на собственные значения.

Файл `.env` содержит секретные данные и не должен попадать в Git.

### 4. Запуск Redis

Пример запуска Redis через Docker:

```powershell
docker run -d --name habit-redis -p 6379:6379 redis:7
```

Если контейнер уже создан и остановлен:

```powershell
docker start habit-redis
```

Проверить доступность Redis:

```powershell
docker exec habit-redis redis-cli ping
```

Ожидаемый ответ: `PONG`.

### 5. Подготовка базы данных

```powershell
poetry run python manage.py migrate
```

При необходимости создать администратора:

```powershell
poetry run python manage.py createsuperuser
```

### 6. Запуск Django

```powershell
poetry run python manage.py runserver
```

API доступен по адресу:

`http://127.0.0.1:8000/`

### 7. Запуск Celery Worker

Открыть отдельный терминал в каталоге проекта:

```powershell
poetry run celery -A config worker --loglevel=info --pool=solo
```

Параметр `--pool=solo` используется для запуска Celery Worker в Windows.

### 8. Запуск Celery Beat

Открыть ещё один терминал:

```powershell
poetry run celery -A config beat --loglevel=info
```

Celery Beat запускает проверку напоминаний каждую минуту. Для доставки уведомлений одновременно должны работать Redis, Celery Worker и Celery Beat.

## API

| Метод | URL | Назначение |
|---|---|---|
| POST | `/api/users/register/` | Регистрация |
| POST | `/api/users/login/` | Получение JWT |
| POST | `/api/users/token/refresh/` | Обновление JWT |
| POST | `/api/users/telegram/` | Привязка Telegram chat ID |
| GET | `/api/habits/` | Список собственных привычек |
| POST | `/api/habits/` | Создание привычки |
| GET | `/api/habits/{id}/` | Просмотр привычки |
| PUT/PATCH | `/api/habits/{id}/` | Изменение привычки |
| DELETE | `/api/habits/{id}/` | Удаление привычки |
| GET | `/api/habits/public/` | Публичные привычки |

Для защищённых запросов необходимо передавать заголовок:

```http
Authorization: Bearer <access_token>
```

Пример создания привычки:

```json
{
  "place": "Home",
  "time": "12:00:00",
  "action": "Drink water",
  "is_pleasant": false,
  "related_habit": null,
  "periodicity": 1,
  "reward": "Tea",
  "duration": 60,
  "is_public": false
}
```

## Telegram

Для получения напоминаний необходимо:

1. Создать Telegram-бота через @BotFather.
2. Указать токен бота в `TELEGRAM_BOT_TOKEN`.
3. Открыть диалог с ботом и отправить `/start` или другое сообщение.
4. Получить свой `chat_id`, например через метод Telegram Bot API `getUpdates`.
5. Авторизоваться в приложении и отправить POST-запрос на `/api/users/telegram/`.

Пример тела запроса:

```json
{
  "chat_id": 123456789
}
```

Привязка выполняется для текущего авторизованного пользователя. Повторная отправка запроса обновляет его `chat_id`. Один идентификатор не может быть привязан к двум пользователям.

**Ограничение:** текущая учебная реализация не подтверждает владение Telegram-аккаунтом. Для использования в публичном сервисе требуется подтверждение через бота или одноразовый код. Не следует привязывать чужие идентификаторы.

## Правила валидации привычек

- Нельзя одновременно указывать вознаграждение и связанную привычку.
- Продолжительность выполнения не может превышать 120 секунд.
- Связанная привычка должна быть приятной.
- Приятная привычка не может иметь вознаграждение или связанную привычку.
- Периодичность должна составлять от 1 до 7 дней.
- Нельзя сделать приятную привычку обычной, если другие привычки используют её как связанную.

## Swagger и OpenAPI

Интерактивная документация:

`http://127.0.0.1:8000/api/docs/`

OpenAPI-схема:

`http://127.0.0.1:8000/api/schema/`

Проверка схемы:

```powershell
poetry run python manage.py spectacular --validate --fail-on-warn
```

## Тестирование

Запуск всех тестов:

```powershell
poetry run pytest -q
```

Проверка покрытия:

```powershell
poetry run pytest --cov=habits --cov=users --cov-report=term-missing
```

Проверка качества и форматирования:

```powershell
poetry run ruff check .
poetry run ruff format --check .
```

Проверка Django:

```powershell
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
```

На момент последней проверки успешно пройдены 37 автоматизированных тестов.

## Структура проекта

```text
project_5/
├── config/             # Настройки Django и Celery
├── habits/             # Модель, API, валидаторы, задачи и тесты привычек
├── users/              # Регистрация, Telegram-профили и API
├── .env.template       # Шаблон переменных окружения
├── pyproject.toml      # Зависимости Poetry и Ruff
├── poetry.lock         # Зафиксированные версии зависимостей
├── pytest.ini          # Конфигурация Pytest
├── manage.py
└── README.md
```

## Примечания

Проект предназначен для учебных целей. Для производственного развёртывания необходимо отдельно настроить безопасное хранение секретов, подтверждение Telegram-аккаунтов, обработку конкурентных запросов и производственную инфраструктуру.