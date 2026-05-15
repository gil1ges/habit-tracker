# Отчёт участника: elyamirazizova

## 1. Общая информация

| Поле | Значение |
|---|---|
| ФИО / GitHub nickname | elyamirazizova |
| Email | emul878@yahoo.com |
| Основная зона ответственности | `analytics`, analytics services, motivational quote API, charts, dashboard, analytics templates/logging |
| Связанные ветки | `origin/feature/analytics-dashboard`, `main` |
| Связанные Django-приложения | `analytics`, частично `habits` как источник данных |
| Связанные шаблоны | `templates/analytics/dashboard.html` |
| Связанные тесты | `tests/test_analytics.py`, fixtures из `tests/conftest.py` |

Краткое описание вклада: участница реализовала аналитический модуль Habit Tracker. Этот модуль собирает статистику по привычкам текущего пользователя, получает мотивирующую цитату через внешний API с fallback и кешированием, строит графики Matplotlib, отображает dashboard и предоставляет JSON endpoint статистики.

По истории Git вклад подтверждается коммитами:

```text
042e5f9 | elyamirazizova <emul878@yahoo.com> | feat: add analytics services
bb1e669 | elyamirazizova <emul878@yahoo.com> | feat: integrate motivational quote API
ec3c8fc | elyamirazizova <emul878@yahoo.com> | feat: add analytics charts
51dbd5a | elyamirazizova <emul878@yahoo.com> | feat: implement analytics dashboard
3925a6b | elyamirazizova <emul878@yahoo.com> | feat: add analytics templates and logging
5be1112 | elyamirazizova <emul878@yahoo.com> | chore: add minimal settings note
```

## 2. Краткое резюме выполненной работы

elyamirazizova отвечала за превращение сырых данных привычек в понятную пользователю аналитику. Приложение `habits` хранит привычки и выполнения, но без отдельного аналитического слоя пользователь видит только список записей. Модуль `analytics` агрегирует эти записи: считает общее число привычек, активные привычки, количество выполнений, выполнения за сегодня, последнюю дату выполнения и сводку по каждой привычке.

Важная архитектурная часть — сервисный слой `analytics/services.py`. Он отделяет бизнес-расчёты от views. Благодаря этому одна и та же статистика используется и в HTML-dashboard, и в JSON endpoint `/analytics/api/stats/`.

Вторая часть — визуализация. Файл `analytics/charts.py` строит несколько типов графиков: столбчатую диаграмму, круговую диаграмму, линейный график, гистограмму и scatter chart. Графики создаются через Matplotlib backend `Agg`, конвертируются в base64 PNG и вставляются прямо в HTML как `data:image/png;base64,...`.

Третья часть — мотивационная цитата. `analytics/external_api.py` обращается к внешнему API `https://api.quotable.io/random` с timeout, проверяет ответ, использует fallback-цитату и кеширует результат на час. Это делает dashboard устойчивым: если внешний сервис недоступен, страница всё равно открывается.

## 3. Файлы и директории, относящиеся к работе участника

| Файл/папка | Назначение | Что реализовано |
|---|---|---|
| `analytics/apps.py` | Конфигурация приложения | Django AppConfig для analytics |
| `analytics/services.py` | Сервисный слой | Расчёт user habit stats, completions by day, completed vs missed |
| `analytics/external_api.py` | Внешняя цитата | Requests к Quotable API, timeout, fallback, cache |
| `analytics/charts.py` | Графики | Matplotlib charts, base64 conversion, empty/error charts |
| `analytics/views.py` | Dashboard и JSON endpoint | `dashboard`, `api_stats`, login protection, logging |
| `analytics/urls.py` | URL analytics | `/analytics/`, `/analytics/api/stats/` |
| `analytics/migrations/__init__.py` | Миграции | Приложение не имеет собственных моделей |
| `templates/analytics/dashboard.html` | HTML dashboard | Карточки статистики, цитата, графики, таблица привычек |
| `tests/test_analytics.py` | Тесты analytics | Auth requirement, dashboard, JSON endpoint, expected keys |
| `habits/models.py` | Источник данных | `Habit` и `HabitCompletion`, которые агрегирует analytics |
| `config/settings.py` | Logging/cache/settings context | Logger `analytics`, Django cache по умолчанию, installed app |

## 4. Подробное описание реализации

### `analytics/services.py`

Файл содержит бизнес-логику расчёта статистики. Он не зависит от HTML и не возвращает `HttpResponse`. Это делает функции переиспользуемыми.

#### `get_user_habit_stats(user) -> dict`

Функция принимает пользователя и возвращает словарь статистики.

Внутри создаётся queryset:

```python
Habit.objects.filter(user=user).annotate(
    completion_count=Count("completions"),
    last_completed=Max("completions__completed_at"),
)
```

Что делает queryset:

- берёт только привычки конкретного пользователя;
- добавляет `completion_count` через `Count`;
- добавляет `last_completed` через `Max`.

Возвращаемые ключи:

- `total_habits` — общее число привычек пользователя;
- `active_habits` — число активных привычек;
- `total_completions` — число всех выполнений пользователя;
- `completed_today` — число выполнений за текущую дату;
- `habits` — список привычек с id, title, frequency, target_count, completion_count, last_completed.

Дата последнего выполнения преобразуется в ISO-формат через `isoformat()`. Если выполнений нет, возвращается `None`.

Эта функция используется:

- в `analytics.views.dashboard`;
- в `analytics.views.api_stats`;
- в `analytics.charts.build_bar_chart`;
- в `analytics.charts.build_histogram`;
- в `analytics.charts.build_scatter_chart`.

#### `get_completion_by_day(user, days: int = 30) -> list[dict]`

Функция строит временной ряд выполнений за последние `days` дней.

Алгоритм:

1. Если `days <= 0`, вернуть пустой список.
2. Вычислить `end_date = timezone.localdate()`.
3. Вычислить `start_date = end_date - timedelta(days=days - 1)`.
4. Отфильтровать `HabitCompletion` по владельцу привычки и диапазону дат.
5. Сгруппировать по `completed_at`.
6. Вернуть список дат от `start_date` до `end_date`, подставляя 0 для дней без выполнений.

Это важно для линейного графика: график должен показывать не только дни с событиями, но и нулевые дни.

#### `get_completed_vs_missed(user, days: int = 30) -> dict`

Функция считает выполненные и условно пропущенные выполнения за период.

Формула:

```text
expected = active_habits * days
missed = max(expected - completed, 0)
```

Возвращает:

- `completed`;
- `missed`.

Эти данные используются в круговой диаграмме.

### `analytics/external_api.py`

Файл отвечает за мотивационную цитату.

Константы:

- `QUOTE_CACHE_KEY = "analytics:motivational_quote"`;
- `QUOTE_CACHE_TIMEOUT = 60 * 60`;
- `FALLBACK_QUOTE` — локальная русскоязычная цитата.

#### `_has_cyrillic(text: str) -> bool`

Вспомогательная функция проверяет наличие кириллицы. В текущей реализации, если внешняя цитата не содержит кириллицу, используется fallback. Это сохраняет русскоязычный интерфейс dashboard.

#### `get_motivational_quote() -> dict`

Алгоритм:

1. Проверить cache по ключу `analytics:motivational_quote`.
2. Если цитата есть в cache, вернуть её.
3. Выполнить `requests.get("https://api.quotable.io/random", timeout=5)`.
4. Вызвать `response.raise_for_status()`.
5. Прочитать JSON.
6. Забрать `content` и `author`.
7. Если цитата не кириллическая, заменить fallback.
8. Если возникли `KeyError`, `ValueError`, `requests.RequestException`, залогировать warning и использовать fallback.
9. Сохранить результат в cache на час.
10. Вернуть словарь с `content` и `author`.

Timeout нужен, чтобы dashboard не зависал надолго при недоступности внешнего API. Fallback нужен, чтобы страница оставалась рабочей. Cache нужен, чтобы не обращаться к API при каждом открытии dashboard.

### `analytics/charts.py`

Файл строит изображения графиков.

В начале указан backend:

```python
matplotlib.use("Agg")
```

`Agg` нужен для серверной среды без GUI. В Docker/Gunicorn нет desktop display, поэтому интерактивные backend-и Matplotlib не подходят.

#### `_fig_to_base64(fig) -> str`

Функция:

1. Создаёт `BytesIO`.
2. Вызывает `fig.tight_layout()`.
3. Сохраняет figure в PNG.
4. Закрывает figure через `plt.close(fig)`.
5. Перематывает buffer.
6. Возвращает base64-строку.

Эта строка вставляется в HTML:

```html
src="data:image/png;base64,{{ bar_chart }}"
```

#### `_build_empty_chart(title, message) -> str`

Строит заглушку, если данных нет. Это лучше, чем показывать сломанный график или пустое место.

#### `_handle_chart_error(chart_name) -> str`

Логирует ошибку с `exc_info=True` и возвращает fallback-график “График недоступен”. Это делает dashboard устойчивым к неожиданным ошибкам в данных или Matplotlib.

#### `build_bar_chart(user) -> str`

Строит столбчатую диаграмму “Выполнения по привычкам”. Использует `get_user_habit_stats(user)`, берёт названия привычек и количество выполнений.

#### `build_pie_chart(user) -> str`

Строит круговую диаграмму “Выполнено и пропущено”. Использует `get_completed_vs_missed(user)`.

#### `build_line_chart(user) -> str`

Строит линейный график выполнений по дням за 30 дней. Использует `get_completion_by_day(user)`.

#### `build_histogram(user) -> str`

Строит гистограмму распределения количества выполнений по привычкам. Использует completion_count из stats.

#### `build_scatter_chart(user) -> str`

Строит scatter chart “Цель и факт выполнения”: по оси X target_count, по оси Y completion_count.

### `analytics/views.py`

Файл связывает сервисы, внешнюю API-цитату, графики и шаблон.

#### `dashboard(request)`

Декоратор `@login_required` требует авторизации. View:

1. Логирует открытие dashboard на уровне `INFO`.
2. Собирает context:
   - `stats`;
   - `quote`;
   - `bar_chart`;
   - `pie_chart`;
   - `line_chart`;
   - `histogram_chart`;
   - `scatter_chart`.
3. Рендерит `templates/analytics/dashboard.html`.

#### `api_stats(request)`

Декоратор `@login_required` требует авторизации. View возвращает JSON:

```python
JsonResponse(get_user_habit_stats(request.user))
```

Если происходит ошибка, view логирует warning с `exc_info=True` и возвращает JSON:

```json
{"detail": "Не удалось загрузить статистику аналитики."}
```

со статусом 500.

Важно: endpoint `/analytics/api/stats/` существует в текущей версии проекта и не должен удаляться.

### `analytics/urls.py`

Маршруты:

```text
GET /analytics/            -> dashboard
GET /analytics/api/stats/  -> api_stats
```

Оба маршрута требуют авторизации на уровне views.

### `templates/analytics/dashboard.html`

Шаблон отображает:

- заголовок “Панель аналитики”;
- кнопку “Открыть данные статистики” на JSON endpoint;
- блок мотивационной цитаты;
- 4 карточки KPI:
  - всего привычек;
  - активных привычек;
  - всего выполнений;
  - выполнено сегодня;
- 5 графиков:
  - bar chart;
  - pie chart;
  - line chart;
  - histogram;
  - scatter chart;
- таблицу “Сводка по привычкам”.

Шаблон использует Bootstrap-карточки и `img src="data:image/png;base64,..."`, поэтому отдельные файлы изображений не создаются.

## 5. Теоретическая база

### Сервисный слой `services.py`

Сервисный слой — это место для бизнес-логики, которую не стоит держать во views. Views должны принимать request и возвращать response, а расчёты лучше выносить в отдельные функции.

Преимущества:

- проще тестировать;
- можно использовать одну функцию в HTML и JSON;
- views остаются читаемыми;
- меньше дублирования.

### Зачем отделять бизнес-логику от views

Если статистика была бы прямо в `dashboard`, то JSON endpoint пришлось бы дублировать. Сейчас `dashboard` и `api_stats` используют `get_user_habit_stats`, поэтому результат согласован.

### Внешний API

Внешний API — сервис вне проекта, к которому приложение обращается по HTTP. В проекте используется `https://api.quotable.io/random`.

### Timeout и fallback

Timeout ограничивает время ожидания ответа. Без timeout пользователь мог бы ждать страницу очень долго.

Fallback — локальный безопасный ответ, который используется при ошибке. Это делает интерфейс устойчивым.

### Кеширование API-ответов

Кеширование сохраняет результат на время. В проекте цитата кешируется на час. Это:

- уменьшает количество внешних запросов;
- ускоряет dashboard;
- снижает риск ошибки при временной недоступности API.

### Matplotlib

Matplotlib — библиотека Python для построения графиков. В веб-проекте она используется на сервере: код строит изображение, сохраняет его в память и отдаёт как base64.

### Как график превращается в base64 image

1. Matplotlib создаёт `Figure`.
2. Figure сохраняется в `BytesIO` в формате PNG.
3. Байты кодируются через `base64.b64encode`.
4. Строка вставляется в HTML `img`.

### Dashboard

Dashboard — аналитическая панель, где пользователь видит агрегированные показатели, визуализации и сводные таблицы. В Habit Tracker dashboard помогает понять прогресс.

### JSON endpoint статистики

JSON endpoint нужен, чтобы статистику можно было получить не только HTML-страницей, но и машинно. `/analytics/api/stats/` возвращает данные, которые можно использовать для frontend, интеграций или отладки.

## 6. Как это работает в проекте

1. Пользователь входит в аккаунт.
2. Открывает `/analytics/`.
3. `analytics.views.dashboard` проверяет авторизацию.
4. View вызывает `get_user_habit_stats(request.user)`.
5. Сервис фильтрует `Habit` и `HabitCompletion` по текущему пользователю.
6. View вызывает `get_motivational_quote()`.
7. Если цитата есть в cache, она берётся из cache.
8. Если cache пуст, происходит запрос к внешнему API.
9. Если внешний API падает, используется fallback.
10. View вызывает функции `build_*_chart`.
11. `charts.py` строит Matplotlib-графики и кодирует их в base64.
12. `dashboard.html` показывает KPI, графики и таблицу.

Сценарий JSON:

1. Пользователь открывает `/analytics/api/stats/`.
2. `api_stats` проверяет авторизацию.
3. Вызывает `get_user_habit_stats`.
4. Возвращает `JsonResponse`.

## 7. Безопасность и ограничения доступа

Оба analytics endpoint защищены:

- `/analytics/` — `@login_required`;
- `/analytics/api/stats/` — `@login_required`.

Статистика фильтруется по `request.user`, поэтому пользователь получает только данные своих привычек:

```python
Habit.objects.filter(user=user)
HabitCompletion.objects.filter(habit__user=user)
```

Это предотвращает утечку чужих данных в dashboard и JSON.

Риски:

- `/analytics/api/stats/` использует session auth, а не токены;
- нет rate limiting на JSON endpoint;
- внешний API цитат может быть недоступен, но fallback уже снижает этот риск;
- графики строятся синхронно при запросе, при большом объёме данных можно вынести построение в cache/background tasks.

В текущей версии `main` отдельный REST endpoint `/api/stats/` не обнаружен; статистика доступна через `/analytics/api/stats/`. REST API реализован в отдельной ветке `feature/rest-api`.

## 8. Валидация данных

Analytics напрямую не принимает пользовательские формы, но зависит от валидности данных `habits`.

Что проверяется косвенно:

- привычки фильтруются по текущему пользователю;
- даты выполнений берутся из `HabitCompletion.completed_at`;
- `days <= 0` в `get_completion_by_day` возвращает пустой список;
- `days <= 0` в `get_completed_vs_missed` возвращает нулевую статистику;
- внешний API проверяется на HTTP status, JSON-структуру и наличие ожидаемых ключей.

Ошибки, которые предотвращаются:

- статистика чужого пользователя;
- падение при пустых привычках;
- падение при недоступном внешнем API;
- зависание dashboard при долгом внешнем запросе.

## 9. Логирование

Logger создаётся в:

- `analytics/views.py`;
- `analytics/charts.py`;
- `analytics/external_api.py`.

События:

- `INFO` — открытие analytics dashboard;
- `WARNING` — ошибка JSON stats endpoint;
- `WARNING` — ошибка получения мотивирующей цитаты;
- `ERROR` — ошибка построения графика с `exc_info=True`.

В `config/settings.py` logger `analytics` подключён к:

- `console`;
- `rotating_file`;
- `timed_file`.

Практическая польза:

- можно понять, открывают ли пользователи dashboard;
- можно увидеть проблемы внешнего API;
- можно диагностировать падения Matplotlib;
- можно искать production-ошибки без воспроизведения вручную.

## 10. Тестирование

К зоне analytics относятся тесты `tests/test_analytics.py`.

Покрытые сценарии:

- dashboard требует авторизации;
- dashboard доступен авторизованному пользователю;
- dashboard получает stats в context;
- внешний quote API и chart builders monkeypatch-ятся, чтобы тест не зависел от сети и Matplotlib;
- `/analytics/api/stats/` возвращает JSON;
- JSON содержит ключи:
  - `total_habits`;
  - `active_habits`;
  - `total_completions`;
  - `completed_today`;
  - `habits`.

Fixtures:

- `authenticated_client`;
- `habit`;
- `completed_habit`.

Запуск:

```bash
python -m pytest tests/test_analytics.py
```

В текущем окружении:

```bash
.venv/bin/python -m pytest tests/test_analytics.py
```

Через Docker:

```bash
docker compose exec web pytest tests/test_analytics.py
```

## 11. Покрытие тестами

Точный процент покрытия не измерен, потому что coverage-инструменты в текущем окружении отсутствуют:

- `pytest-cov` не установлен;
- `coverage` не установлен;
- системная команда `python` отсутствует.

Фактический полный тестовый прогон:

```text
46 passed in 3.14s
```

Команда:

```bash
.venv/bin/python -m pytest
```

Команда для измерения покрытия после установки:

```bash
python -m pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

Лучше всего покрыты:

- доступ к dashboard;
- JSON endpoint;
- структура статистики.

Хуже покрыты:

- `analytics/services.py` отдельными unit-тестами;
- `analytics/external_api.py` с ошибками API/cache;
- реальные функции `analytics/charts.py`;
- HTML-детали dashboard.

Что можно улучшить:

- добавить unit-тесты `get_completion_by_day`;
- добавить unit-тесты `get_completed_vs_missed`;
- добавить тест fallback quote;
- добавить тест cache quote;
- добавить тест `_build_empty_chart`.

## 12. Docker / запуск / эксплуатация

Analytics работает внутри Docker как часть Django service `web`.

Важные моменты:

- Matplotlib использует backend `Agg`, поэтому не требует GUI.
- В `Dockerfile` задано `MPLCONFIGDIR=/tmp/matplotlib`.
- При сборке создаётся директория `/tmp/matplotlib`.
- Логи analytics пишутся в `/app/logs`, который связан с volume `logs_data`.
- Внешний API цитат требует сетевой доступ из контейнера.

Запуск:

```bash
docker compose up -d --build
```

Проверка dashboard:

```text
http://server-ip/analytics/
```

Проверка JSON:

```text
http://server-ip/analytics/api/stats/
```

Оба URL требуют входа в аккаунт.

## 13. Команды для проверки работы

Локально:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py runserver
python -m pytest tests/test_analytics.py
```

В текущем окружении:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_analytics.py
```

Docker:

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose logs -f web
```

Ручная проверка:

```text
/analytics/
/analytics/api/stats/
```

## 14. Возможные проблемы и способы решения

### Dashboard требует вход

Это ожидаемо: view защищён `@login_required`. Нужно войти через `/auth/login/`.

### На dashboard нет данных

Проверить:

- созданы ли привычки;
- выполнены ли привычки;
- принадлежит ли привычка текущему пользователю.

### Не строятся графики

Проверить логи:

```bash
docker compose logs -f web
```

Возможные причины:

- ошибка данных;
- проблема Matplotlib;
- нет прав на `MPLCONFIGDIR`;
- слишком большой объём данных.

В текущей реализации при ошибке должен появиться fallback-график “График недоступен”.

### Внешний API недоступен

`external_api.py` должен использовать fallback. Проверить warning в логах. Dashboard не должен падать.

### JSON endpoint возвращает 500

Проверить `logs/app.log` или Docker logs. Возможная причина — ошибка в данных или запросах к БД.

### В Docker нет графиков

Проверить:

- установлен ли `matplotlib` из `requirements.txt`;
- задан ли `MPLCONFIGDIR`;
- контейнер пересобран после изменения requirements.

### Данные чужого пользователя видны

В текущем коде статистика фильтруется по `request.user`. Если такая проблема появилась, проверить изменения в `analytics/services.py` и fixtures/данные.

## 15. Что можно улучшить

- Добавить кэширование готовых графиков.
- Добавить выбор периода: 7/30/90 дней.
- Добавить streaks и процент выполнения целей.
- Добавить REST API `/api/stats/` в основную ветку после review ветки `feature/rest-api`.
- Добавить Swagger для analytics endpoints.
- Добавить export CSV/JSON.
- Добавить больше unit-тестов services.
- Добавить тесты fallback quote и cache.
- Вынести тяжёлые графики в background tasks через Celery.
- Добавить интерактивные графики на frontend.

## 16. Итоговый вклад участника

elyamirazizova реализовала аналитический слой Habit Tracker: сервисы расчёта статистики, внешний API мотивирующей цитаты с timeout/cache/fallback, построение графиков Matplotlib, dashboard с KPI и визуализациями, JSON endpoint статистики и логирование analytics-событий. Этот вклад делает проект не просто списком привычек, а инструментом анализа прогресса пользователя.
