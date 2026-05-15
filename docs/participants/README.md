# Документация по вкладу участников

Этот раздел содержит подробные отчёты по зонам ответственности участников команды Habit Tracker. Документация подготовлена по фактической структуре проекта, текущему коду, шаблонам, тестам, Docker/deploy-файлам и истории Git.

## 1. Общая архитектура проекта

Habit Tracker — классическое Django-приложение с server-rendered HTML templates, session-based authentication и SQLite по умолчанию.

Основные слои:

| Слой | Файлы/модули | Назначение |
|---|---|---|
| Project config | `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py` | Общие настройки, корневая маршрутизация, WSGI/ASGI |
| Core | `core/views.py`, `core/urls.py`, `templates/core/home.html` | Главная страница |
| Users/Auth | `users/*`, `templates/registration/*`, `templates/users/register.html` | `CustomUser`, регистрация, login/logout/password reset/change |
| Habits | `habits/*`, `templates/habits/*` | Модели привычек, CRUD, формы, выполнение привычек |
| Analytics | `analytics/*`, `templates/analytics/dashboard.html` | Статистика, цитата, графики, dashboard, JSON stats |
| Utils | `utils/validators.py` | Regex validators и функции нормализации |
| Tests | `pytest.ini`, `tests/*` | Pytest-django, fixtures, unit/integration tests |
| Deploy | `Dockerfile`, `docker-compose.yml`, `deploy/nginx.conf`, `.env.example` | Docker Compose, Gunicorn, Nginx, volumes, SMTP env |
| Docs | `README.md`, `docs/participants/*` | Общая и персональная документация |

Текущая ветка `main`, от которой создана эта документация, не содержит подключённого DRF REST API под `/api/`. REST API обнаружен в отдельной ветке `feature/rest-api`; в персональных отчётах он упоминается как отдельная ветка/возможное улучшение, а не как часть текущего `main`.

## 2. Таблица участников

| Участник | Email | Краткая зона ответственности |
|---|---|---|
| Dmitriy Prihodin | d.prihodin816@gmail.com | Инициализация Django-проекта, `users`, `core`, `CustomUser`, регистрация, авторизация, auth templates, auth logging/email backend |
| Hayden2572 | nikitaborisovv353@gmail.com | `habits`, `Habit`, `HabitCompletion`, формы, валидаторы привычек, CRUD, шаблоны habits, README, Docker/deploy, SMTP |
| elyamirazizova | emul878@yahoo.com | `analytics`, services, motivational quote API, charts, dashboard, analytics templates/logging |
| Aleksandra-dan | alex.kvashko@mail.ru | `utils` validators, pytest, fixtures, user/habit/analytics tests, logging, integration/conflict fixes |

## 3. Ссылки на персональные README

- [Отчёт Dmitriy Prihodin](README_DMITRIY_PRIHODIN.md)
- [Отчёт Hayden2572](README_HAYDEN2572.md)
- [Отчёт elyamirazizova](README_ELYAMIRAZIZOVA.md)
- [Отчёт Aleksandra-dan](README_ALEKSANDRA_DAN.md)

## 4. Карта модулей проекта

| Участник | Приложение/модуль | Ветка/источник | Функционал |
|---|---|---|---|
| Dmitriy Prihodin | `config` | `feature/project-bootstrap`, `origin/feature/users-auth`, `main` | Django skeleton, settings, root urls |
| Dmitriy Prihodin | `core` | `feature/project-bootstrap`, `origin/feature/users-auth`, `main` | Главная страница `/` |
| Dmitriy Prihodin | `users` | `origin/feature/users-auth`, `main` | `CustomUser`, registration flow, auth signals, admin |
| Dmitriy Prihodin | `templates/registration`, `templates/users` | `origin/feature/users-auth`, `main` | Login/logout/password reset/change/register templates |
| Hayden2572 | `habits` | `origin/feature/habits-crud`, `main` | Habit/HabitCompletion, forms, validators, CRUD, complete |
| Hayden2572 | `templates/habits` | `origin/feature/habits-crud`, `main` | List/detail/form/delete templates |
| Hayden2572 | `README.md` | `readme-ru`, `main` | Общая документация проекта |
| Hayden2572 | Docker/deploy | `main` | `Dockerfile`, `docker-compose.yml`, Nginx, volumes |
| Hayden2572 | SMTP env | `main` | `.env.example`, email backend variables |
| elyamirazizova | `analytics/services.py` | `origin/feature/analytics-dashboard`, `main` | Расчёт статистики |
| elyamirazizova | `analytics/external_api.py` | `origin/feature/analytics-dashboard`, `main` | Quote API, timeout, fallback, cache |
| elyamirazizova | `analytics/charts.py` | `origin/feature/analytics-dashboard`, `main` | Matplotlib charts, base64 PNG |
| elyamirazizova | `analytics/views.py`, `analytics/urls.py` | `origin/feature/analytics-dashboard`, `main` | Dashboard и `/analytics/api/stats/` |
| elyamirazizova | `templates/analytics/dashboard.html` | `origin/feature/analytics-dashboard`, `main` | KPI, цитата, графики, таблица |
| Aleksandra-dan | `utils/validators.py` | `origin/feature/tests-logging`, `main` | Regex validators и normalizers |
| Aleksandra-dan | `tests` | `origin/feature/tests-logging`, `main` | Pytest fixtures и тесты |
| Aleksandra-dan | `config/settings.py` | `origin/feature/tests-logging`, `main` | Logging config |
| Aleksandra-dan | Integration | `main` | Merge/conflict fixes users/habits/analytics/tests |

## 5. Как проверить проект

Базовая проверка Django:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
```

В текущем рабочем окружении системная команда `python` отсутствовала, поэтому фактически использовалась команда из virtualenv:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py migrate
```

Запуск локального сервера:

```bash
python manage.py runserver
```

Основные страницы для ручной проверки:

```text
/
/auth/login/
/auth/register/
/habits/
/analytics/
/analytics/api/stats/
```

## 6. Как запустить через Docker

Проект запускается через Docker Compose.

Сервисы:

| Сервис | Назначение |
|---|---|
| `web` | Django + Gunicorn |
| `nginx` | Reverse proxy, порт `80`, static/media |

Запуск:

```bash
docker compose up -d --build
```

Логи:

```bash
docker compose logs -f
docker compose logs -f web
docker compose logs -f nginx
```

Миграции:

```bash
docker compose exec web python manage.py migrate
```

Создание суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

Сборка статики:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Остановка:

```bash
docker compose down
```

В текущем `docker-compose.yml` отдельного сервиса БД нет. Используется SQLite-файл в volume `sqlite_data`.

## 7. Как запустить тесты

Полный прогон:

```bash
python -m pytest
```

В текущем окружении:

```bash
.venv/bin/python -m pytest
```

Фактический результат на момент подготовки документации:

```text
46 passed in 3.14s
```

По модулям:

```bash
python -m pytest tests/test_users.py
python -m pytest tests/test_habits.py
python -m pytest tests/test_analytics.py
python -m pytest tests/test_regex_validators.py
```

Через Docker:

```bash
docker compose exec web pytest
```

## 8. Как посмотреть покрытие

Сначала была выполнена команда:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

Она не выполнилась, потому что в окружении отсутствует системная команда `python`.

Затем была выполнена команда:

```bash
.venv/bin/python -m pytest --cov=. --cov-report=term-missing
```

Она не выполнилась, потому что `pytest-cov` не установлен.

Запасной вариант:

```bash
.venv/bin/python -m coverage run -m pytest
```

тоже не выполнился, потому что пакет `coverage` не установлен.

Точный процент покрытия в текущей версии документации не указан и не выдуман.

Чтобы измерить покрытие, нужно установить инструмент:

```bash
python -m pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

Или через coverage:

```bash
python -m pip install coverage
coverage run -m pytest
coverage report -m
```

Ожидаемо лучше всего покрыты:

- `utils/validators.py`;
- пользовательские auth-сценарии;
- CRUD привычек;
- analytics dashboard/API на уровне integration tests.

Ожидаемо хуже покрыты:

- templates;
- admin classes;
- logging side effects;
- Matplotlib chart internals;
- external API fallback/cache;
- Docker/deploy.

## 9. Как использовать документацию на защите

Рекомендуемый порядок:

1. Начать с этого индексного README и показать общую архитектуру.
2. Перейти к персональному README участника.
3. В разделе “Файлы и директории” показать конкретные файлы в проекте.
4. В разделе “Подробное описание реализации” объяснить код: классы, функции, связи.
5. В разделе “Теоретическая база” ответить на вопросы преподавателя.
6. В разделе “Как это работает” рассказать пользовательский сценарий.
7. В разделе “Безопасность” показать, как защищены данные.
8. В разделе “Тестирование” показать pytest-команды и результат.
9. Для Hayden2572 отдельно показать Docker/Deploy/SMTP.
10. Для Aleksandra-dan отдельно показать Integration / Conflict Fixes.

Короткая схема защиты по ролям:

| Участник | Что показывать в коде | Что объяснять теоретически |
|---|---|---|
| Dmitriy Prihodin | `users/models.py`, `users/forms.py`, `users/views.py`, `config/settings.py`, auth templates | Django project/app, CustomUser, AUTH_USER_MODEL, sessions, email backend |
| Hayden2572 | `habits/models.py`, `habits/forms.py`, `habits/views.py`, Docker files | Model, ForeignKey, ModelForm, CRUD, owner protection, Docker/SMTP |
| elyamirazizova | `analytics/services.py`, `analytics/external_api.py`, `analytics/charts.py`, dashboard template | Service layer, API timeout/fallback/cache, Matplotlib, dashboard, JSON |
| Aleksandra-dan | `utils/validators.py`, `tests/*`, `config/settings.py` logging | Regex, pytest, fixtures, parametrization, logging handlers, integration fixes |

## Дополнительная информация из Git history

История подтверждает разделение ответственности:

- Dmitriy Prihodin сделал старт проекта и users/auth.
- Hayden2572 сделал habits, README, deploy и SMTP.
- elyamirazizova сделала analytics.
- Aleksandra-dan сделала tests/logging и integration fixes.

Обнаруженные integration commits:

```text
354d60d Merge remote-tracking branch 'origin/feature/users-auth'
bfddc4c merge: resolve habits integration conflicts
7473d91 merge: resolve analytics integration conflicts
b61ffda merge: resolve tests integration conflicts
```

Обнаруженная отдельная API-ветка:

```text
feature/rest-api
origin/feature/rest-api
```

В текущем `main` приложение `api` не подключено, поэтому документация участников описывает фактический код `main`, а REST API указывается как дальнейшее улучшение или отдельная ветка.
