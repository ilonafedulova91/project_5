# Habit Tracker API

Backend-приложение для отслеживания полезных привычек с автоматическими напоминаниями через Telegram.

Проект разработан на Django и Django REST Framework. Пользователи могут создавать, просматривать, редактировать и удалять собственные привычки, просматривать публичные привычки других пользователей и получать напоминания по расписанию.

## Технологии

- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- PostgreSQL — основная база данных при запуске через Docker Compose
- SQLite — для локальной разработки без Docker
- Redis
- Celery Worker и Celery Beat
- Nginx
- Docker и Docker Compose
- Telegram Bot API
- drf-spectacular (Swagger/OpenAPI)
- django-cors-headers
- Poetry
- Pytest, pytest-django, pytest-cov
- Ruff
- GitHub Actions

## Функциональность

- Регистрация пользователей и JWT-аутентификация.
- CRUD-операции с привычками.
- Ограничение доступа к привычкам их владельцем.
- Публичный список привычек с доступом без авторизации.
- Пагинация по пять записей по умолчанию.
- Валидация продолжительности, периодичности, вознаграждений и связанных приятных привычек.
- Автоматические Telegram-напоминания через Celery.
- Привязка Telegram chat ID к авторизованному пользователю.
- Документация API через Swagger/OpenAPI.

## Архитектура Docker Compose

Проект включает следующие сервисы:

| Сервис | Назначение |
|---|---|
| `web` | Django-приложение, запущенное через Gunicorn |
| `db` | PostgreSQL и постоянное хранение данных |
| `redis` | Брокер сообщений и backend результатов Celery |
| `celery_worker` | Выполнение фоновых задач |
| `celery_beat` | Планирование периодических задач |
| `nginx` | Приём HTTP-запросов и обслуживание статических файлов |

Все сервисы запускаются одной командой через Docker Compose.

## Требования

Для запуска через Docker необходимы:

- Git
- Docker Desktop с поддержкой Docker Compose (Windows/macOS) либо Docker Engine и Docker Compose Plugin (Linux)

Для локальной разработки без Docker дополнительно необходимы Python 3.12, Poetry и Redis.

## Локальный запуск через Docker Compose

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd project_5
```

Замените `<repository-url>` адресом вашего GitHub-репозитория.

### 2. Настройка переменных окружения

Создайте `.env` на основе шаблона.

Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

Linux/macOS:

```bash
cp .env.template .env
```

Откройте `.env` и задайте собственные значения:

```dotenv
SECRET_KEY=replace-with-a-secure-random-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost

TIME_ZONE=Europe/Athens
CORS_ALLOWED_ORIGINS=

TELEGRAM_BOT_TOKEN=replace-with-your-bot-token

DB_ENGINE=postgres
POSTGRES_DB=habit_tracker
POSTGRES_USER=habit_user
POSTGRES_PASSWORD=replace-with-a-long-random-password
```

Используйте сильный уникальный пароль PostgreSQL и собственный Django `SECRET_KEY`.

Файл `.env` содержит конфиденциальные данные и не должен попадать в Git.

Если приложение будет доступно по доменному имени или внешнему IP-адресу, добавьте соответствующий адрес в `ALLOWED_HOSTS` серверного `.env`.

### 3. Запуск всех сервисов

Из корневого каталога проекта выполните:

```bash
docker compose up -d --build
```

Команда собирает необходимые образы и запускает Django, PostgreSQL, Redis, Celery Worker, Celery Beat и Nginx.

При запуске Django выполняет миграции и собирает статические файлы перед запуском Gunicorn.

Проверить состояние сервисов:

```bash
docker compose ps
```

Посмотреть логи всех сервисов:

```bash
docker compose logs -f
```

Посмотреть логи Django:

```bash
docker compose logs -f web
```

### 4. Создание администратора

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Доступ к приложению

После успешного запуска:

- Django-приложение через Nginx: http://localhost/
- Панель администратора: http://localhost/admin/
- Swagger: http://localhost/api/docs/
- OpenAPI-схема: http://localhost/api/schema/

### 6. Остановка проекта

Остановить сервисы:

```bash
docker compose down
```

Данные PostgreSQL хранятся в именованном Docker volume и сохраняются при обычной остановке контейнеров.

**Важно:** команда `docker compose down -v` удаляет именованные тома проекта, что может привести к потере данных. Не используйте её, если данные нужно сохранить.

## Локальная разработка без Docker

SQLite можно использовать для разработки вне Docker, если переменная `DB_ENGINE` не установлена в значение `postgres`.

### 1. Установка зависимостей

```bash
poetry install
```

### 2. Настройка окружения

Создайте `.env` на основе `.env.template` и настройте необходимые переменные.

Для подключения к Redis, запущенному отдельно от приложения, используйте адрес `localhost`.

### 3. Миграции

```bash
poetry run python manage.py migrate
```

При необходимости создайте администратора:

```bash
poetry run python manage.py createsuperuser
```

### 4. Запуск Django

```bash
poetry run python manage.py runserver
```

### 5. Запуск Celery Worker

В отдельном терминале:

```bash
poetry run celery -A config worker --loglevel=info --pool=solo
```

Параметр `--pool=solo` подходит для запуска Celery Worker в Windows.

### 6. Запуск Celery Beat

В другом терминале:

```bash
poetry run celery -A config beat --loglevel=info
```

Для отправки напоминаний должны работать Redis, Celery Worker и Celery Beat.

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

## Telegram-напоминания

Для получения напоминаний необходимо:

1. Создать Telegram-бота через [@BotFather](https://t.me/BotFather).
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

Привязка выполняется для текущего авторизованного пользователя. Повторная отправка запроса обновляет его chat ID. Один идентификатор не может быть привязан к двум пользователям.

Текущая учебная реализация не подтверждает владение Telegram-аккаунтом. Для публичного сервиса рекомендуется подтверждение через бота или одноразовый код.

## Правила валидации привычек

- Нельзя одновременно указывать вознаграждение и связанную привычку.
- Продолжительность выполнения не может превышать 120 секунд.
- Связанная привычка должна быть приятной.
- Приятная привычка не может иметь вознаграждение или связанную привычку.
- Периодичность должна составлять от 1 до 7 дней.
- Нельзя сделать приятную привычку обычной, если другие привычки используют её как связанную.

## Swagger и OpenAPI

Интерактивная документация:

http://localhost/api/docs/

OpenAPI-схема:

http://localhost/api/schema/

Проверка схемы:

```bash
poetry run python manage.py spectacular --validate --fail-on-warn
```

## Тестирование и качество кода

Установка зависимостей для разработки:

```bash
poetry install --with dev
```

Запуск всех тестов:

```bash
poetry run pytest
```

Проверка покрытия:

```bash
poetry run pytest --cov=habits --cov=users --cov-report=term-missing
```

Проверка качества кода:

```bash
poetry run ruff check .
```

Проверка форматирования:

```bash
poetry run ruff format --check .
```

Проверка Django:

```bash
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
```

В ходе локальной проверки проекта успешно прошли 37 автоматизированных тестов, а Ruff не обнаружил ошибок.

## CI/CD через GitHub Actions

Конфигурация pipeline находится в `.github/workflows/ci-cd.yml`.

Pipeline выполняет следующие этапы:

1. **Tests:** устанавливает зависимости, запускает PostgreSQL и выполняет автоматизированные тесты.
2. **Lint:** проверяет качество кода с помощью Ruff.
3. **Build:** проверяет конфигурацию Docker Compose и возможность сборки Docker-образа приложения.
4. **Deploy:** после успешного завершения предыдущих этапов выполняет автоматический деплой при push в ветку `main`.

Изменения в `feature` и pull request в `develop` запускают проверки, но не запускают production-деплой.

### Настройка GitHub Secrets

В настройках GitHub-репозитория откройте **Settings → Secrets and variables → Actions** и добавьте:

| Secret | Значение |
|---|---|
| `SSH_HOST` | Публичный IP-адрес или доменное имя сервера |
| `SSH_USER` | Имя пользователя на сервере |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ для подключения к серверу |

Не добавляйте реальные пароли, приватные ключи или токены непосредственно в YAML-файл workflow.

## Настройка удалённого сервера и деплой

Для деплоя необходим сервер с установленными Docker, Docker Compose Plugin и Git.

### 1. Подготовка проекта на сервере

Клонируйте репозиторий в каталог, ожидаемый workflow, — `~/project_5`:

```bash
git clone <repository-url> ~/project_5
cd ~/project_5
```

Убедитесь, что пользователь сервера может запускать необходимые Docker-команды без интерактивного ввода пароля. SSH-подключение GitHub Actions должно работать без ручного подтверждения.

### 2. Настройка серверного окружения

Создайте на сервере `.env` на основе `.env.template` и задайте реальные значения:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS` с адресом сервера или доменом
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `TELEGRAM_BOT_TOKEN`, если используются Telegram-напоминания

Серверный `.env` не должен попадать в Git.

### 3. Первый запуск на сервере

Из каталога проекта выполните:

```bash
docker compose up -d --build
```

Проверьте состояние сервисов:

```bash
docker compose ps
docker compose logs --tail=100
```

Убедитесь, что приложение доступно и миграции завершились без ошибок.

### 4. Автоматический деплой

После настройки SSH-доступа и GitHub Secrets workflow автоматически выполняет деплой при push в `main`, если тесты, линтинг и сборка завершились успешно.

В рамках деплоя сервер получает актуальный код ветки `main` и запускает:

```bash
docker compose up -d --build
```

Результат каждого запуска можно проверить в разделе **Actions** репозитория GitHub.

Перед переходом с существующей SQLite-базы на PostgreSQL необходимо сделать резервную копию и определить, нужно ли переносить имеющиеся данные. Создание новой PostgreSQL-базы само по себе не переносит данные из SQLite.

## Структура проекта

```text
project_5/
├── config/                 # Настройки Django и Celery
├── habits/                 # Привычки, API, задачи и тесты
├── users/                  # Пользователи и Telegram-интеграция
├── nginx/                  # Конфигурация Nginx
├── .github/workflows/      # GitHub Actions
├── .env.template           # Шаблон переменных окружения
├── docker-compose.yml      # Конфигурация сервисов
├── Dockerfile              # Образ Django-приложения
├── pyproject.toml          # Зависимости Poetry и Ruff
├── poetry.lock             # Зафиксированные зависимости
├── pytest.ini              # Конфигурация Pytest
├── manage.py
└── README.md
```

## Примечания по безопасности

- Не коммитьте `.env` и другие файлы с секретами.
- Не используйте учебные пароли в production.
- Перед изменением базы данных на существующем сервере сделайте резервную копию.
- Для публичного production-развёртывания настройте HTTPS, например с помощью TLS-сертификата и соответствующей конфигурации Nginx.
- Регулярно проверяйте состояние контейнеров и логи приложения.
