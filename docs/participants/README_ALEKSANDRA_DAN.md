# Отчёт участника: Aleksandra-dan

## 1. Общая информация

| Поле | Значение |
|---|---|
| ФИО / GitHub nickname | Aleksandra-dan |
| Email | alex.kvashko@mail.ru |
| Основная зона ответственности | validators utils, pytest, fixtures, user tests, habit tests, analytics tests, logging, integration/conflict fixes |
| Связанные ветки | `origin/feature/tests-logging`, `main` |
| Связанные Django-приложения | `utils`, `tests`, частично `config`, `users`, `habits`, `analytics` |
| Связанные тесты | `tests/conftest.py`, `tests/test_users.py`, `tests/test_habits.py`, `tests/test_analytics.py`, `tests/test_regex_validators.py` |
| Связанные настройки | `pytest.ini`, `config/settings.py` |

Краткое описание вклада: участница отвечала за тестовую инфраструктуру, регулярные validators utils, общие fixtures, тесты пользовательских сценариев, CRUD привычек, аналитики, настройку pytest, проектное логирование и интеграционные исправления после объединения функциональных веток.

По истории Git вклад подтверждается коммитами:

```text
ff20981 | Aleksandra-dan <alex.kvashko@mail.ru> | feat: add regex validators utils
325eb88 | Aleksandra-dan <alex.kvashko@mail.ru> | test: configure pytest and fixtures
1d10ad5 | Aleksandra-dan <alex.kvashko@mail.ru> | test: add user authentication tests
ebf210a | Aleksandra-dan <alex.kvashko@mail.ru> | test: add habit tests
c7f816f | Aleksandra-dan <alex.kvashko@mail.ru> | test: add analytics tests
3bd2f0d | Aleksandra-dan <alex.kvashko@mail.ru> | chore: configure project logging
354d60d | Aleksandra-dan <alex.kvashko@mail.ru> | Merge remote-tracking branch 'origin/feature/users-auth'
bfddc4c | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve habits integration conflicts
7473d91 | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve analytics integration conflicts
b61ffda | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve tests integration conflicts
5f2b653 | Aleksandra-dan <alex.kvashko@mail.ru> | fix: add users field alignment migration
efe9d52 | Aleksandra-dan <alex.kvashko@mail.ru> | feat: improve template content
9665d57 | Aleksandra-dan <alex.kvashko@mail.ru> | feat: enhance admin model metadata
ed159f5 | Aleksandra-dan <alex.kvashko@mail.ru> | feat: refine interface content
```

## 2. Краткое резюме выполненной работы

Aleksandra-dan обеспечила качество и интеграционную устойчивость проекта. После реализации отдельных функциональных веток проекту нужны были автоматические тесты, общие fixtures, проверка доступов, проверка CRUD-сценариев и контроль, что analytics не ломается при изменениях в habits/users.

В `utils/validators.py` добавлен набор regex-валидаторов и функций нормализации: проверка логина, поиск дат в тексте, парсинг лог-строки, проверка сложности пароля, проверка email по доменам, нормализация телефона. Эти функции не привязаны к Django-моделям и могут переиспользоваться в разных частях проекта.

В `tests/` настроены pytest-django fixtures. Они создают пользователей, привычки, авторизованный client и completion. Благодаря этому тесты стали короче и стабильнее.

Тесты проверяют:

- регистрацию, login, logout, password change;
- доступность и защиту CRUD привычек;
- запрет доступа к чужим привычкам;
- создание completion и защиту от дублей;
- dashboard analytics;
- JSON endpoint статистики;
- regex validators utils.

В `config/settings.py` настроена система logging с console/file handlers и отдельными loggers для `django`, `users`, `habits`, `analytics`.

Также в истории Git видны явные интеграционные commits, связанные с merge/conflict fixes. Это означает, что зона ответственности включала не только написание тестов, но и приведение веток к совместимому состоянию.

## 3. Файлы и директории, относящиеся к работе участника

| Файл/папка | Назначение | Что реализовано |
|---|---|---|
| `utils/validators.py` | Утилитарные regex validators | Login regex, date extraction, log parsing, password check, email domain check, phone normalization |
| `utils/__init__.py` | Python package marker | Делает `utils` импортируемым пакетом |
| `pytest.ini` | Конфигурация pytest | `DJANGO_SETTINGS_MODULE`, шаблон имён тестовых файлов |
| `tests/conftest.py` | Общие fixtures | `user`, `another_user`, `authenticated_client`, `habit`, `completed_habit`, `TEST_PASSWORD` |
| `tests/test_users.py` | Auth/user tests | Регистрация, validation error, login, logout, password change |
| `tests/test_habits.py` | Habit tests | Auth requirement, create/update/delete, owner protection, complete, duplicate completion |
| `tests/test_analytics.py` | Analytics tests | Dashboard auth, dashboard context, JSON stats, expected keys |
| `tests/test_regex_validators.py` | Unit tests validators | Parametrized tests for all utility validators |
| `config/settings.py` | Logging config | `LOGGING`, handlers, formatters, loggers |
| `users/migrations/0003_alter_customuser_options_alter_customuser_avatar_and_more.py` | User model alignment migration | Field/options alignment after integration |
| `users/admin.py` | Admin metadata | Расширение отображения CustomUser в admin |
| `habits/admin.py` | Admin metadata | Отображение Habit/HabitCompletion в admin |
| `templates/base.html` | Общий UI после интеграции | Навигация, auth controls, messages |

## 4. Подробное описание реализации

### `utils/validators.py`

Файл содержит независимые от Django utilities.

#### Regex-константы

`LOGIN_RE`:

```python
r"^[A-Za-z][A-Za-z0-9_]{3,18}[A-Za-z0-9]$"
```

Правило:

- логин начинается с латинской буквы;
- внутри допускаются латинские буквы, цифры и `_`;
- длина ограничена;
- логин не заканчивается `_`.

`DATE_RE` ищет даты формата:

- `1.2.24`;
- `10-12-2025`;
- `05/06/2024`.

Regex использует backreference `\1`, чтобы разделитель был одинаковым внутри одной даты.

`LOG_RE` парсит лог-строку формата:

```text
YYYY-MM-DD HH:MM:SS LEVEL user=<user> action=<action> ip=<ip>
```

Он содержит named groups: `date`, `time`, `level`, `user`, `action`, `ip`.

`EMAIL_RE` проверяет базовый формат email. `PASSWORD_SPECIAL_RE` ищет спецсимвол из набора `[!@#$%^&*]`.

#### `validate_login(login: str) -> bool`

Возвращает `True`, если login полностью соответствует `LOGIN_RE`.

#### `find_dates(text: str) -> list[str]`

Находит все даты в тексте и возвращает список строк. Использует `DATE_RE.finditer`.

#### `parse_log(log: str) -> dict`

Парсит лог-строку. Если строка не соответствует формату, выбрасывает `ValueError("Unsupported log format.")`. Если соответствует, возвращает словарь named groups.

#### `validate_password(password: str) -> bool`

Проверяет:

- длина минимум 8;
- есть uppercase;
- есть lowercase;
- есть digit;
- есть спецсимвол.

#### `validate_email_domain(email: str, domains: list[str]) -> bool`

Сначала проверяет email regex-ом. Затем сравнивает домен email со списком разрешённых доменов без учёта регистра.

#### `normalize_phone(phone: str) -> str`

Удаляет все нецифровые символы. Принимает только 11 цифр, начинающихся на `7` или `8`, и возвращает формат `+7XXXXXXXXXX`. Если формат неподдерживаемый, выбрасывает `ValueError`.

### `pytest.ini`

Файл настраивает pytest-django:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

`DJANGO_SETTINGS_MODULE` сообщает pytest, какие Django settings использовать. `python_files` определяет, какие файлы считать тестовыми.

### `tests/conftest.py`

Файл содержит fixtures, доступные тестам.

Fixtures:

- `user(db)` — создаёт `CustomUser` с `username`, `email`, password и phone;
- `another_user(db)` — второй пользователь для проверки доступа;
- `authenticated_client(client, user)` — Django test client с `force_login`;
- `habit(user)` — привычка текущего пользователя;
- `completed_habit(habit)` — выполнение привычки за текущую дату.

`TEST_PASSWORD = "StrongPass1!"` используется как общий валидный пароль.

Fixtures снижают дублирование. Вместо повторного создания пользователя в каждом тесте тест запрашивает `user` или `authenticated_client`.

### `tests/test_users.py`

Проверяет auth/users:

- `test_successful_registration` — POST на `register`, создание пользователя, redirect на `habit_list`, запись `_auth_user_id` в session;
- `test_registration_validation_error` — короткий username и пустой email не создают пользователя, форма содержит ошибки;
- `test_successful_login` — стандартный login создаёт session;
- `test_logout_redirect` — POST logout редиректит на `home` и очищает session;
- `test_password_change_page_available_for_authenticated_user` — авторизованный пользователь видит страницу смены пароля.

### `tests/test_habits.py`

Проверяет habits:

- список привычек требует auth;
- создание привычки сохраняет owner;
- update меняет поля;
- delete удаляет запись;
- чужая привычка возвращает 404;
- complete создаёт `HabitCompletion`;
- повторный complete за тот же день не создаёт дубль.

Эти тесты особенно важны, потому что проверяют безопасность доступа к пользовательским данным.

### `tests/test_analytics.py`

Проверяет analytics:

- dashboard требует auth;
- авторизованный пользователь получает dashboard;
- context содержит stats;
- quote API и chart functions monkeypatch-ятся;
- `/analytics/api/stats/` возвращает JSON;
- JSON содержит ожидаемые ключи.

Monkeypatch нужен, чтобы тесты не зависели от внешнего API и реального построения графиков.

### `tests/test_regex_validators.py`

Файл содержит parametrized tests для `utils.validators`.

Проверяются:

- валидные и невалидные логины;
- поиск дат;
- парсинг валидных логов;
- ошибка на невалидных логах;
- сложность пароля;
- email domain;
- нормализация телефона;
- ошибка на неправильном телефоне.

Parametrized tests позволяют проверить много входных значений коротко и читаемо.

### `config/settings.py`

В зоне Aleksandra находится logging config.

Компоненты:

- `LOG_DIR` создаётся из `DJANGO_LOG_DIR` или `BASE_DIR / "logs"`;
- formatters:
  - `verbose`;
  - `simple`;
- handlers:
  - `console`;
  - `rotating_file`;
  - `timed_file`;
- loggers:
  - `django`;
  - `users`;
  - `habits`;
  - `analytics`.

Такой logging config покрывает как локальную разработку, так и эксплуатацию в Docker.

## 5. Теоретическая база

### Regex validators

Regex validators используют регулярные выражения для проверки строк. Они хороши для форматов: login, email, дата, лог-строка. Важно применять `fullmatch`, когда строка должна соответствовать шаблону целиком.

### Pytest

Pytest — тестовый фреймворк Python. Он автоматически находит тесты, запускает функции `test_*`, показывает понятные assert errors и поддерживает fixtures.

### Fixtures

Fixtures — подготовленные объекты или состояния для тестов. В pytest fixture объявляется функцией с `@pytest.fixture`, а тест получает её по имени аргумента.

### Parametrized tests

Parametrized tests позволяют запустить один тест с несколькими наборами данных. В проекте это используется для validators: разные логины, пароли, email, телефоны.

### Unit и integration tests

Unit tests проверяют маленькую функцию изолированно, например `validate_password`.

Integration tests проверяют взаимодействие частей системы, например POST на `/habits/create/`, сохранение модели и redirect.

### Тестирование доступа

Тестирование доступа проверяет, что защищённые страницы требуют login, а пользователь не может получить чужие данные. В проекте это проверяется для `/habits/`, чужой привычки и analytics dashboard.

### Logging

Logging — система записи событий приложения. Она помогает отлаживать, аудитить действия и расследовать ошибки.

### StreamHandler

`StreamHandler` пишет логи в поток, обычно stdout/stderr. В Docker это удобно: логи видны через `docker compose logs`.

### RotatingFileHandler

`RotatingFileHandler` пишет в файл и ротирует его при достижении размера. В проекте `maxBytes=1048576`, `backupCount=5`.

### TimedRotatingFileHandler

`TimedRotatingFileHandler` ротирует файл по времени. В проекте используется `when="midnight"` и `backupCount=7`.

### Integration/conflict fixes

Integration/conflict fixes — работа по объединению веток, где менялись одни и те же файлы или взаимосвязанные модули. Нужно привести settings, urls, templates, tests и migrations к состоянию, где проект стартует и тесты проходят.

## 6. Как это работает в проекте

### Pytest flow

1. Pytest читает `pytest.ini`.
2. `pytest-django` поднимает тестовую БД.
3. Fixtures из `tests/conftest.py` создают пользователей, привычки и completions.
4. Тесты отправляют HTTP-запросы через Django test client.
5. Django views выполняют реальные проверки, формы и ORM-операции.
6. Assertions проверяют status code, redirects, database state, JSON keys.
7. После тестов тестовая БД очищается.

### Logging flow

1. Код вызывает `logging.getLogger(__name__)`.
2. Python logging поднимается к logger name.
3. В `config/settings.py` logger `users`, `habits`, `analytics` связан с handlers.
4. Сообщение форматируется formatter-ом.
5. Сообщение пишется в console, `logs/app.log`, `logs/daily.log`.

### Validators flow

1. В функцию передаётся строка.
2. Regex проверяет формат.
3. Функция возвращает `True`/`False`, список, словарь или нормализованную строку.
4. Если формат критично неверный, функция выбрасывает `ValueError`.

## 7. Безопасность и ограничения доступа

В зоне тестов проверяются важные security-сценарии:

- `/habits/` требует авторизации;
- чужая привычка возвращает 404;
- dashboard analytics требует авторизации;
- регистрация не создаёт пользователя при невалидной форме;
- logout очищает session.

Это не сами security-механизмы, но автоматическая проверка, что они работают.

Связанные модули:

- `users` отвечает за session auth;
- `habits` отвечает за owner protection;
- `analytics` фильтрует статистику по user;
- `config/settings.py` задаёт auth redirects и password validators.

Оставшиеся риски:

- нет тестов CSRF;
- нет тестов password reset email flow;
- нет тестов logging side effects;
- нет coverage threshold;
- нет CI, который запускал бы тесты на каждый push.

## 8. Валидация данных

В `utils/validators.py` проверяются:

- login format;
- даты в тексте;
- формат лог-строки;
- сложность пароля;
- формат email и разрешённый домен;
- формат телефона.

В тестах проверяются:

- валидные и невалидные значения;
- исключения для неправильных логов и телефонов;
- регистронезависимость email domain.

Кроме utils, тесты indirectly проверяют:

- валидацию регистрации;
- валидацию привычек через формы;
- уникальность completion за день.

## 9. Логирование

Logging config находится в `config/settings.py`.

Formatters:

- `verbose`: уровень, время, модуль, process, thread, message;
- `simple`: уровень и message.

Handlers:

- `console` — поток вывода;
- `rotating_file` — файл `logs/app.log`, ротация по размеру;
- `timed_file` — файл `logs/daily.log`, ротация по дням.

Loggers:

- `django`;
- `users`;
- `habits`;
- `analytics`.

Уровни:

- `INFO` — нормальные бизнес-события;
- `WARNING` — подозрительные или нежелательные события;
- `ERROR` — ошибки, требующие внимания.

В текущих тестах логирование как side effect отдельно не assert-ится. Это можно улучшить через pytest `caplog`.

## 10. Тестирование

Основные команды:

```bash
python -m pytest
python -m pytest tests/test_users.py
python -m pytest tests/test_habits.py
python -m pytest tests/test_analytics.py
python -m pytest tests/test_regex_validators.py
```

В текущем окружении:

```bash
.venv/bin/python -m pytest
```

Через Docker:

```bash
docker compose exec web pytest
```

Фактический результат:

```text
46 passed in 3.14s
```

Сценарии:

- unit tests для validators;
- integration tests для auth;
- integration tests для habits CRUD;
- integration tests для analytics dashboard/API.

## 11. Покрытие тестами

Точный процент покрытия не измерен.

Причины:

```text
python -m pytest --cov=. --cov-report=term-missing
```

не выполнен, потому что системная команда `python` отсутствует.

```text
.venv/bin/python -m pytest --cov=. --cov-report=term-missing
```

не выполнен, потому что `pytest-cov` не установлен.

```text
.venv/bin/python -m coverage run -m pytest
```

не выполнен, потому что `coverage` не установлен.

Команда для измерения после установки:

```bash
python -m pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

Лучше всего покрыты:

- `utils/validators.py`;
- основные auth-сценарии;
- основные habit CRUD-сценарии;
- analytics endpoint structure.

Хуже покрыты:

- Django admin classes;
- templates;
- logging side effects;
- charts internals;
- external API fallback/cache;
- Docker/deploy.

## 12. Docker / запуск / эксплуатация

Тесты и logging работают в Docker без отдельной настройки:

- `pytest` установлен из `requirements.txt`;
- `DJANGO_SETTINGS_MODULE` берётся из `pytest.ini`;
- логи пишутся в `/app/logs`, volume `logs_data`;
- тесты внутри контейнера можно запускать командой `docker compose exec web pytest`.

Команды:

```bash
docker compose up -d --build
docker compose exec web pytest
docker compose exec web python manage.py check
docker compose logs -f web
```

Для production важно смотреть логи не только Django, но и Nginx:

```bash
docker compose logs -f nginx
```

## 13. Команды для проверки работы

Проверка Django:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
```

Проверка тестов:

```bash
python -m pytest
```

В текущем окружении:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest
```

Docker:

```bash
docker compose up -d --build
docker compose exec web python manage.py check
docker compose exec web python manage.py migrate
docker compose exec web pytest
docker compose logs -f
```

Проверка логов:

```bash
tail -n 100 logs/app.log
tail -n 100 logs/daily.log
docker compose logs --tail=100 web
```

## 14. Возможные проблемы и способы решения

### Pytest падает из-за БД

Проверить, установлен ли `pytest-django` и задан ли `DJANGO_SETTINGS_MODULE` в `pytest.ini`.

```bash
python -m pip install -r requirements.txt
python -m pytest
```

### Fixture не найдена

Проверить, что fixture находится в `tests/conftest.py`, а тест запускается из root проекта.

### Тест login падает

Проверить password fixture `TEST_PASSWORD`, пользователя и `LOGIN_REDIRECT_URL`.

### Тест привычек падает на 404

Проверить owner: привычка должна принадлежать пользователю, который залогинен в `authenticated_client`.

### Analytics test обращается во внешний API

В тесте dashboard используется `monkeypatch`. Если тест начал ходить в сеть, проверить patch targets:

```python
analytics.views.get_motivational_quote
analytics.views.build_bar_chart
```

### Логи не пишутся

Проверить, создана ли директория `logs/` и есть ли права на запись. В Docker проверить volume `logs_data`.

### Docker container не стартует после merge

Запустить:

```bash
docker compose logs -f web
docker compose logs -f nginx
```

Затем проверить:

```bash
python manage.py check
python manage.py makemigrations --check
python -m pytest
```

## 15. Что можно улучшить

- Добавить `pytest-cov` и coverage threshold.
- Добавить CI/CD с pytest, check и makemigrations --check.
- Добавить тесты logging через `caplog`.
- Добавить тесты password reset email.
- Добавить тесты forms validators отдельно.
- Добавить тесты analytics services без monkeypatch dashboard.
- Добавить тесты external API fallback/cache.
- Добавить тесты Docker healthcheck.
- Добавить pre-commit hooks.
- Слить и протестировать DRF REST API из `feature/rest-api`.

# Integration / Conflict Fixes

## Какие conflict-fix commits видны в истории

В истории Git обнаружены явные commits интеграции и разрешения конфликтов:

```text
354d60d | Aleksandra-dan <alex.kvashko@mail.ru> | Merge remote-tracking branch 'origin/feature/users-auth'
bfddc4c | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve habits integration conflicts
7473d91 | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve analytics integration conflicts
b61ffda | Aleksandra-dan <alex.kvashko@mail.ru> | merge: resolve tests integration conflicts
f3307da | Aleksandra-dan <alex.kvashko@mail.ru> | chore: restore app source from feature branches
```

Это значит, что интеграционная работа в проекте действительно была, а не только теоретически описывается.

## Какие конфликтные зоны обычно были в проекте

### `settings.py`

Конфликтная зона, потому что разные участники добавляли:

- приложения в `INSTALLED_APPS`;
- auth settings;
- email settings;
- static/media;
- logging;
- database path через env;
- deploy settings.

После merge нужно проверять, что все приложения остались подключены:

```python
"core",
"users",
"habits",
"analytics",
```

И что `AUTH_USER_MODEL = "users.CustomUser"` не потерялся.

### `urls.py`

Конфликтная зона, потому что разные ветки добавляли:

- `/`;
- `/auth/`;
- `/habits/`;
- `/analytics/`;
- `/admin/`.

После merge нужно проверять, что два подключения `/auth/` сохранились: стандартные auth URLs и `users.urls`.

### `base.html`

Конфликтная зона, потому что общий layout нужен всем:

- users добавляет login/register/logout;
- habits добавляет навигацию к привычкам;
- analytics добавляет навигацию к аналитике;
- UI-правки меняют тексты и Bootstrap-разметку.

После merge нужно проверить, что nav links не ведут на несуществующие route names.

### `requirements.txt`

Конфликтная зона, потому что разные участники добавляли зависимости:

- Django;
- Pillow;
- pytest;
- pytest-django;
- requests;
- matplotlib;
- gunicorn.

После merge важно не удалить зависимость другого модуля. Например analytics требует `requests` и `matplotlib`, deploy требует `gunicorn`, avatar требует `Pillow`.

### `tests`

Конфликтная зона, потому что tests зависят от маршрутов, моделей и redirects. Например после добавления `habits` регистрация стала редиректить на `habit_list`, а тесты users должны учитывать это.

### `logging`

Конфликтная зона, потому что разные приложения создают logger через `__name__`, а settings должен содержать loggers `users`, `habits`, `analytics`.

## Как проверялась интеграция

Минимальная интеграционная проверка:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python -m pytest
```

В текущем окружении фактически используется:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest
```

Проверка URL вручную:

```text
/
/auth/login/
/auth/register/
/habits/
/analytics/
/analytics/api/stats/
```

Проверка Docker:

```bash
docker compose up -d --build
docker compose logs -f
```

## Как убедиться, что проект после merge работает

1. Проверить ветку:

```bash
git status
git branch
```

2. Установить зависимости:

```bash
python -m pip install -r requirements.txt
```

3. Проверить Django config:

```bash
python manage.py check
```

4. Проверить миграции:

```bash
python manage.py makemigrations --check
python manage.py migrate
```

5. Запустить тесты:

```bash
python -m pytest
```

6. Запустить приложение:

```bash
python manage.py runserver
```

7. Проверить основные страницы:

```text
/
/auth/login/
/auth/register/
/habits/
/analytics/
```

8. Проверить Docker:

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 web
```

## Какие integration fixes видны по текущей структуре

По текущей структуре видно, что интеграция сохранила:

- единый `CustomUser` как `AUTH_USER_MODEL`;
- связь `Habit.user` с `settings.AUTH_USER_MODEL`;
- analytics, работающую поверх `Habit` и `HabitCompletion`;
- общие templates и navigation;
- общий logging config;
- pytest fixtures, которые работают для users/habits/analytics;
- Docker Compose, который запускает всё приложение целиком.

## 16. Итоговый вклад участника

Aleksandra-dan обеспечила тестовую и интеграционную надёжность Habit Tracker: добавила regex validators utils, настроила pytest-django, написала fixtures и тесты для users, habits, analytics и validators, настроила проектное логирование и выполнила интеграционные merge/conflict fixes между функциональными ветками. Её вклад позволяет проверять проект автоматически и безопаснее объединять изменения разных участников.
