# Отчёт участника: Hayden2572

## 1. Общая информация

| Поле | Значение |
|---|---|
| ФИО / GitHub nickname | Hayden2572 |
| Email | nikitaborisovv353@gmail.com |
| Основная зона ответственности | `habits`, модели `Habit` и `HabitCompletion`, формы и валидация привычек, CRUD привычек, шаблоны habits, README, Docker/deploy, SMTP настройки |
| Связанные ветки | `origin/feature/habits-crud`, `readme-ru`, `origin/readme-ru`, `main`, дополнительно `feature/rest-api` как отдельная неслитая API-ветка |
| Связанные Django-приложения | `habits`, частично `config`, `analytics`, `users` через связи |
| Связанные шаблоны | `templates/habits/*.html` |
| Связанные deploy-файлы | `Dockerfile`, `docker-compose.yml`, `deploy/nginx.conf`, `.env.example`, `.dockerignore` |
| Связанные тесты | `tests/test_habits.py`, fixtures из `tests/conftest.py` |

Краткое описание вклада: участник реализовал доменную часть Habit Tracker — создание, редактирование, удаление и выполнение привычек. Кроме Django-логики, зона Hayden2572 включает пользовательские формы, валидаторы привычек, шаблоны интерфейса, документацию README и production-oriented запуск через Docker Compose, Gunicorn и Nginx. Также в проект добавлены SMTP-переменные окружения для отправки писем, используемых стандартными auth-сценариями Django.

По истории Git вклад подтверждается коммитами:

```text
af2b9ee | Hayden2572 <nikitaborisovv353@gmail.com> | feat: create habit models
2c8d49f | Hayden2572 <nikitaborisovv353@gmail.com> | feat: add habit validation and forms
edf38c2 | Hayden2572 <nikitaborisovv353@gmail.com> | feat: implement habit CRUD views
1571ba0 | Hayden2572 <nikitaborisovv353@gmail.com> | feat: add habit templates
7602972 | Hayden2572 <nikitaborisovv353@gmail.com> | chore: add habit logging
d11eb7d | Hayden2572 <nikitaborisovv353@gmail.com> | docs: add readme and localize interface
d4cf9c7 | Hayden2572 <nikitaborisovv353@gmail.com> | deploychutchut
250734c | Hayden2572 <nikitaborisovv353@gmail.com> | Fix gunicorn control socket in docker compose
7cfc395 | Hayden2572 <nikitaborisovv353@gmail.com> | Add SMTP email settings
24032ec | Hayden2572 <nikitaborisovv353@gmail.com> | delete trash files
```

Также в истории есть отдельная ветка `feature/rest-api` с коммитами Hayden2572 по REST API. В текущей ветке `main`, от которой создан этот отчёт, приложение `api` и DRF-настройки не обнаружены; поэтому REST API описывается как отдельная ветка/возможное улучшение, а не как часть текущей реализации `main`.

## 2. Краткое резюме выполненной работы

Hayden2572 реализовал основной пользовательский функционал трекера привычек. Именно через приложение `habits` пользователь создаёт привычки, задаёт периодичность и цель, выбирает цвет, временно отключает привычку, просматривает список своих привычек, открывает подробную карточку, редактирует и удаляет записи.

Вторая важная часть — выполнение привычек. Модель `HabitCompletion` хранит факт выполнения конкретной привычки за конкретную дату. Ограничение `unique_together = ["habit", "completed_at"]` не позволяет создать два выполнения одной привычки за один день. Это делает статистику корректной и предотвращает случайные дубли.

CRUD-слой построен на Django class-based views: `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`. Доступ ограничивается авторизацией и проверкой владельца объекта. Пользователь видит только свои привычки, а попытка открыть чужую привычку возвращает 404 и логируется.

Отдельный вклад — Docker/deploy. Проект можно запустить в контейнерах: сервис `web` отвечает за Django/Gunicorn, сервис `nginx` принимает HTTP на 80 порту и проксирует запросы в Django. SQLite, media, static, logs и sent emails сохраняются в Docker volumes.

README проекта содержит инструкции по локальному запуску, Docker Compose, деплою на сервер, структуре проекта, маршрутам и основным сценариям. SMTP-настройки вынесены в `.env.example`, чтобы письма восстановления пароля могли отправляться через внешний почтовый сервер.

## 3. Файлы и директории, относящиеся к работе участника

| Файл/папка | Назначение | Что реализовано |
|---|---|---|
| `habits/models.py` | Доменные модели привычек | `Habit`, `HabitCompletion`, связь с пользователем, частотность, уникальность выполнения по дате |
| `habits/forms.py` | Формы Django | `HabitForm`, `HabitCompletionForm`, widgets, labels, help texts, clean-валидация |
| `habits/validators.py` | Валидаторы привычек | Проверка title, target_count, HEX color, запрещённых слов |
| `habits/views.py` | CRUD и выполнение | CBV для списка/деталей/создания/обновления/удаления, `habit_complete`, проверка владельца, logging |
| `habits/urls.py` | URL приложения привычек | `/habits/`, create/detail/edit/delete/complete |
| `habits/admin.py` | Django admin | Отображение, фильтры и поиск Habit/HabitCompletion |
| `habits/apps.py` | Конфигурация приложения | AppConfig для `habits` |
| `habits/migrations/*.py` | Миграции БД | Создание и изменение таблиц Habit/HabitCompletion |
| `templates/habits/habit_list.html` | Список привычек | Карточки привычек, кнопки CRUD, empty state |
| `templates/habits/habit_detail.html` | Детальная карточка | Информация о привычке, форма выполнения, история completions |
| `templates/habits/habit_form.html` | Создание/редактирование | Универсальная форма Habit |
| `templates/habits/habit_confirm_delete.html` | Удаление | Подтверждение удаления привычки |
| `tests/test_habits.py` | Тесты привычек | Auth requirement, create/update/delete, owner access, complete, duplicate protection |
| `tests/conftest.py` | Общие fixtures | Пользователи, авторизованный client, habit, completed_habit |
| `README.md` | Главная документация | Описание проекта, запуск, deploy, URL, структура, CRUD |
| `Dockerfile` | Сборка Django-образа | Python 3.13 slim, установка requirements, Gunicorn, non-root user |
| `docker-compose.yml` | Оркестрация контейнеров | `web`, `nginx`, volumes, migrate/collectstatic/gunicorn |
| `deploy/nginx.conf` | Nginx | Reverse proxy, static/media aliases, headers |
| `.env.example` | Пример production env | Django, DB path, static/media/log dirs, email/SMTP |
| `.dockerignore` | Docker build context | Исключение локальных/служебных файлов из build context |
| `requirements.txt` | Python-зависимости | Django, Pillow, pytest, requests, matplotlib, gunicorn |

## 4. Подробное описание реализации

### `habits/models.py`

Файл описывает главные бизнес-сущности проекта.

#### `Habit`

`Habit` представляет привычку пользователя. Поля:

- `user` — `ForeignKey` на `settings.AUTH_USER_MODEL`, владелец привычки;
- `title` — название, максимум 100 символов, валидируется `validate_habit_title` и `validate_forbidden_words`;
- `description` — необязательное описание;
- `frequency` — периодичность из `FrequencyChoices`: `daily`, `weekly`, `monthly`;
- `target_count` — целевое количество выполнений за период;
- `color` — HEX-цвет вида `#RRGGBB`;
- `is_active` — активна ли привычка;
- `created_at` — дата создания;
- `updated_at` — дата обновления.

`FrequencyChoices` реализован через `models.TextChoices`. Это даёт фиксированный набор допустимых значений в базе и человекочитаемые подписи для форм/шаблонов.

`user = models.ForeignKey(..., related_name="habits")` создаёт связь “один пользователь — много привычек”. Благодаря `related_name` можно писать `request.user.habits.all()`.

`get_absolute_url()` возвращает URL детальной страницы привычки:

```python
reverse("habit_detail", kwargs={"pk": self.pk})
```

Это используется `CreateView` и `UpdateView` для redirect после успешного сохранения.

#### `HabitCompletion`

`HabitCompletion` хранит факт выполнения привычки:

- `habit` — `ForeignKey` на `Habit`, связь “одна привычка — много выполнений”;
- `completed_at` — дата выполнения, по умолчанию `timezone.localdate`;
- `note` — необязательная короткая заметка;
- `created_at` — дата создания записи.

В `Meta` задано:

```python
unique_together = ["habit", "completed_at"]
ordering = ["-completed_at"]
```

Уникальность предотвращает дубль выполнения одной привычки за один день. Сортировка показывает последние выполнения первыми.

### `habits/validators.py`

Файл содержит доменные валидаторы привычек.

`FORBIDDEN_WORDS = ("bad", "spam", "test123")` задаёт список запрещённых слов. `HEX_COLOR_RE` проверяет цвет строго в формате `#RRGGBB`.

Функции:

- `validate_habit_title(value)` — title после strip должен быть минимум 3 символа;
- `validate_target_count(value)` — target count должен быть от 1 до 30;
- `validate_color(value)` — цвет должен соответствовать regex `^#[0-9A-Fa-f]{6}$`;
- `validate_forbidden_words(value)` — текст не должен содержать запрещённые слова.

Валидаторы используются и на уровне модели, и в форме `HabitForm`. Это снижает риск сохранить некорректные данные из разных точек входа.

### `habits/forms.py`

Файл реализует формы для HTML-интерфейса.

#### `HabitForm`

`HabitForm` — `ModelForm` для модели `Habit`. Поля:

- `title`;
- `description`;
- `frequency`;
- `target_count`;
- `color`;
- `is_active`.

В `Meta` настроены labels, help texts и widgets. Widgets добавляют Bootstrap-классы и placeholder-ы, чтобы форма была удобной и понятной.

Методы clean:

- `clean_title()` — strip, проверка длины и запрещённых слов;
- `clean_target_count()` — диапазон 1..30;
- `clean_color()` — HEX формат;
- `clean_description()` — strip и проверка запрещённых слов;
- `clean()` — межполевая логика.

Межполевая логика:

- если `frequency == daily`, `target_count` не должен быть больше 7;
- если `is_active is False`, описание обязательно.

Это хорошая реализация, потому что часть правил зависит не от одного поля, а от комбинации значений.

#### `HabitCompletionForm`

Форма содержит только поле `note`. Дата выполнения не вводится пользователем: view `habit_complete` всегда отмечает текущую дату. Это упрощает UX и предотвращает случайное создание выполнения на неправильный день через HTML-форму.

### `habits/views.py`

Файл реализует основной CRUD и защиту доступа.

#### `OwnerHabitQuerysetMixin`

Mixin наследуется от `LoginRequiredMixin`. Он ограничивает queryset привычками текущего пользователя:

```python
return Habit.objects.filter(user=self.request.user)
```

`get_object()` дополнительно делает явную проверку:

1. Находит привычку по `pk`.
2. Если привычки нет, возвращает 404.
3. Если привычка существует, но принадлежит другому пользователю, пишет warning в лог и возвращает 404.
4. Если владелец совпадает, возвращает объект из owner-filtered queryset.

Такой подход не раскрывает факт существования чужой привычки. Пользователь получает “не найдено”, а не “доступ запрещён к существующему объекту”.

#### `HabitListView`

Показывает список привычек текущего пользователя. Наследуется от `LoginRequiredMixin` и `ListView`, использует шаблон `habits/habit_list.html`.

`get_queryset()` возвращает:

```python
self.request.user.habits.all()
```

Это использует `related_name="habits"` из модели `Habit`.

#### `HabitDetailView`

Показывает одну привычку и добавляет в context `completion_form`. Благодаря `OwnerHabitQuerysetMixin` пользователь может открыть только свою привычку.

#### `HabitCreateView`

Создаёт привычку через `HabitForm`. В `form_valid()` до сохранения присваивает:

```python
form.instance.user = self.request.user
```

Это критично: пользователь не выбирает owner руками, owner всегда берётся из session.

После сохранения пишется `INFO` с user_id, habit_id и title.

#### `HabitUpdateView`

Редактирует привычку. Доступ ограничен owner mixin. После успешного сохранения логируется `INFO`.

#### `HabitDeleteView`

Удаляет привычку владельца. Использует шаблон подтверждения и после удаления возвращает на `habit_list`. Удаление логируется как `WARNING`, потому что это потенциально важное событие с потерей данных.

#### `habit_complete`

Function-based view для отметки привычки выполненной сегодня.

Декораторы:

- `@login_required`;
- `@require_POST`.

Алгоритм:

1. Получить привычку по `pk`.
2. Проверить владельца.
3. Прочитать `note` из POST.
4. Выполнить `HabitCompletion.objects.get_or_create(habit=habit, completed_at=timezone.localdate(), defaults={"note": note})`.
5. Если запись создана, залогировать выполнение.
6. Если запись уже была, залогировать пропуск дубля.
7. Вернуть redirect на detail page.

`get_or_create` вместе с unique constraint делает операцию устойчивой к повторному нажатию кнопки.

### `habits/urls.py`

Маршруты:

```text
GET  /habits/                 список привычек
GET  /habits/create/          форма создания
POST /habits/create/          создание
GET  /habits/<pk>/            detail
GET  /habits/<pk>/edit/       форма редактирования
POST /habits/<pk>/edit/       обновление
GET  /habits/<pk>/delete/     подтверждение удаления
POST /habits/<pk>/delete/     удаление
POST /habits/<pk>/complete/   выполнение за сегодня
```

### `habits/admin.py`

Файл регистрирует модели в Django admin.

`HabitAdmin` показывает title, user, frequency, target_count, is_active, поддерживает фильтры по frequency/is_active и поиск по title/description/user.

`HabitCompletionAdmin` показывает habit, completed_at, created_at, поддерживает фильтр по completed_at и поиск по habit title/note.

### `templates/habits/habit_list.html`

Шаблон списка привычек. Если привычки есть, показывает Bootstrap-карточки с:

- названием;
- периодичностью;
- статусом active/pause;
- описанием;
- target_count;
- color;
- кнопками “Подробнее”, “Редактировать”, “Удалить”.

Если привычек нет, показывает empty state и кнопку добавления первой привычки.

### `templates/habits/habit_detail.html`

Шаблон детальной страницы. Показывает:

- title;
- frequency display;
- active/inactive badge;
- description;
- target_count;
- color swatch;
- created_at/updated_at;
- форму отметки выполнения;
- историю выполнений.

История использует `object.completions.all`, то есть related_name из `HabitCompletion.habit`.

### `templates/habits/habit_form.html`

Универсальный шаблон создания и редактирования привычки. Он выводит поля `HabitForm`, CSRF, ошибки полей и кнопки сохранения/возврата.

### `templates/habits/habit_confirm_delete.html`

Шаблон подтверждения удаления. Это важно для UX: пользователь должен явно подтвердить destructive-действие.

### `README.md`

README описывает проект, стек, локальный запуск, Docker Compose deploy, структуру файлов, маршруты, CRUD привычек, аналитику и тесты. Документация пригодна для запуска проекта другим участником или преподавателем.

### `Dockerfile`

Dockerfile строит образ Django-приложения:

1. Базовый образ `python:3.13-slim`.
2. Переменные `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`, `PIP_NO_CACHE_DIR`, `MPLCONFIGDIR`.
3. Рабочая директория `/app`.
4. Копирование `requirements.txt`.
5. Установка зависимостей.
6. Копирование проекта.
7. Создание non-root пользователя `app`.
8. Создание директорий `/app/data`, `/app/media`, `/app/staticfiles`, `/app/logs`, `/app/sent_emails`.
9. Запуск Gunicorn на `0.0.0.0:8000`.

### `docker-compose.yml`

Compose описывает два сервиса:

- `web` — Django/Gunicorn;
- `nginx` — reverse proxy.

Сервис `web` перед стартом выполняет:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --no-control-socket
```

Сервис `nginx` публикует порт `80:80`, отдаёт static/media и проксирует остальные запросы в `web:8000`.

### `deploy/nginx.conf`

Nginx:

- слушает порт 80;
- имеет `server_name 188.187.214.161 _`;
- отдаёт `/static/` из `/app/staticfiles/`;
- отдаёт `/media/` из `/app/media/`;
- проксирует `/` в `http://web:8000`;
- передаёт заголовки `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.

### `.env.example`

Файл показывает production-переменные:

- Django secret/debug/hosts/csrf;
- пути DB/static/media/email/logs;
- SMTP backend и credentials.

Фактический `.env` не должен попадать в Git.

## 5. Теоретическая база

### Django Model

Django Model описывает таблицу базы данных в Python-коде. Поля модели превращаются в колонки таблицы, а методы модели описывают поведение объекта. В проекте `Habit` и `HabitCompletion` являются моделями.

### ForeignKey

`ForeignKey` описывает связь “многие к одному”. В проекте:

- много привычек принадлежат одному пользователю;
- много выполнений принадлежат одной привычке.

### One-to-Many связь

One-to-Many — это когда один объект связан со многими объектами другого типа. Пример: один `CustomUser` имеет много `Habit`; одна `Habit` имеет много `HabitCompletion`.

### ModelForm

`ModelForm` автоматически строит HTML-форму на основе модели. Он умеет валидировать данные и сохранять объект. `HabitForm` связан с `Habit`, `HabitCompletionForm` связан с `HabitCompletion`.

### Validators

Validators — функции, которые проверяют значение и выбрасывают `ValidationError`, если значение некорректно. Они нужны, чтобы защищать базу от плохих данных.

### CRUD

CRUD означает:

- Create — создание;
- Read — просмотр;
- Update — редактирование;
- Delete — удаление.

В `habits` CRUD реализован через class-based views.

### LoginRequiredMixin

`LoginRequiredMixin` запрещает доступ неавторизованным пользователям к class-based views. Если пользователь не вошёл, Django отправляет его на `LOGIN_URL`.

### Ограничение доступа к чужим объектам

Доступ ограничивается owner-filtered queryset:

```python
Habit.objects.filter(user=self.request.user)
```

И дополнительной проверкой в `get_object()`. Чужая привычка возвращает 404.

### Docker и docker-compose

Docker упаковывает приложение и зависимости в контейнер. Docker Compose описывает несколько контейнеров и связи между ними. В проекте Compose запускает Django и Nginx.

### SMTP в веб-проекте

SMTP нужен для отправки email. В этом проекте он используется прежде всего стандартными Django views восстановления пароля. SMTP-настройки вынесены в `.env`.

## 6. Как это работает в проекте

### Создание привычки

1. Пользователь входит в аккаунт.
2. Открывает `/habits/create/`.
3. `HabitCreateView` показывает `HabitForm`.
4. Пользователь отправляет POST.
5. `HabitForm` валидирует title, description, frequency, target_count, color, is_active.
6. `form_valid()` присваивает `form.instance.user = request.user`.
7. Habit сохраняется.
8. Событие логируется.
9. Пользователь попадает на `/habits/<pk>/`.

### Просмотр списка привычек

1. Пользователь открывает `/habits/`.
2. `HabitListView` требует login.
3. `get_queryset()` возвращает только `request.user.habits.all()`.
4. `habit_list.html` показывает карточки.

### Редактирование привычки

1. Пользователь открывает `/habits/<pk>/edit/`.
2. `OwnerHabitQuerysetMixin` проверяет владельца.
3. Если привычка чужая, возвращает 404.
4. Если привычка своя, показывает форму.
5. После POST форма валидируется и объект сохраняется.

### Выполнение привычки

1. Пользователь открывает detail page.
2. Вводит note или оставляет пустым.
3. Отправляет POST на `/habits/<pk>/complete/`.
4. `habit_complete` проверяет login, POST и владельца.
5. Создаётся `HabitCompletion` на сегодняшнюю дату.
6. Повторный POST в тот же день не создаёт дубль.
7. Пользователь возвращается на detail page.

## 7. Безопасность и ограничения доступа

Страницы habits требуют авторизации:

- `/habits/`;
- `/habits/create/`;
- `/habits/<pk>/`;
- `/habits/<pk>/edit/`;
- `/habits/<pk>/delete/`;
- `/habits/<pk>/complete/`.

Механизмы защиты:

- `LoginRequiredMixin` для class-based views;
- `@login_required` для `habit_complete`;
- `@require_POST` для выполнения привычки;
- `OwnerHabitQuerysetMixin` для detail/update/delete;
- ручная проверка owner в `habit_complete`;
- 404 вместо раскрытия существования чужой привычки;
- CSRF в HTML-формах;
- логирование попыток доступа к чужим объектам.

В текущей версии `main` REST API под `/api/` не обнаружен. API-защита JWT реализована только в отдельной ветке `feature/rest-api`.

Оставшиеся риски:

- можно добавить rate limiting на выполнение привычек;
- можно добавить soft delete вместо физического удаления;
- можно добавить audit trail для всех изменений;
- можно расширить права в admin.

## 8. Валидация данных

Валидируются:

- `title` — минимум 3 символа, запрещённые слова;
- `description` — запрещённые слова;
- `target_count` — от 1 до 30;
- `color` — формат `#RRGGBB`;
- `frequency + target_count` — daily не больше 7;
- `is_active + description` — неактивная привычка должна иметь описание;
- `HabitCompletion` — уникальность habit/date на уровне БД.

Валидация предотвращает:

- пустые или слишком короткие названия;
- мусорный цвет;
- завышенные цели;
- запрещённый текст;
- дубли выполнений;
- неконсистентные данные для аналитики.

## 9. Логирование

Logger создаётся в `habits/views.py`:

```python
logger = logging.getLogger(__name__)
```

Логируются:

- `INFO` — создание привычки;
- `INFO` — обновление привычки;
- `WARNING` — удаление привычки;
- `INFO` — выполнение привычки;
- `INFO` — повторное выполнение в тот же день пропущено;
- `WARNING` — попытка доступа к чужой привычке.

В `config/settings.py` logger `habits` подключён к handlers:

- `console`;
- `rotating_file`;
- `timed_file`.

Практическая польза: можно отследить пользовательские действия, диагностировать ошибки доступа и понимать, какие изменения происходили в данных.

## 10. Тестирование

К зоне Hayden2572 относятся `tests/test_habits.py`.

Покрытые сценарии:

- список привычек требует авторизации;
- создание привычки;
- редактирование привычки;
- удаление привычки;
- пользователь не может открыть чужую привычку;
- отметка выполнения;
- повторная отметка в тот же день не создаёт дубль.

Fixtures из `tests/conftest.py`:

- `user`;
- `another_user`;
- `authenticated_client`;
- `habit`;
- `completed_habit`.

Запуск:

```bash
python -m pytest tests/test_habits.py
```

В текущем окружении:

```bash
.venv/bin/python -m pytest tests/test_habits.py
```

Через Docker:

```bash
docker compose exec web pytest tests/test_habits.py
```

## 11. Покрытие тестами

Точный процент покрытия не измерен: `pytest-cov` и `coverage` в текущем окружении не установлены, а системная команда `python` отсутствует.

Фактический полный прогон:

```text
46 passed in 3.14s
```

Команда:

```bash
.venv/bin/python -m pytest
```

Как измерить покрытие:

```bash
python -m pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

Лучше всего в зоне Hayden покрыты CRUD-сценарии и owner protection. Хуже покрыты:

- отдельные validators в `habits/validators.py`;
- шаблоны как HTML;
- admin classes;
- edge cases `HabitForm.clean()`;
- Docker/deploy не покрываются pytest.

## 12. Docker / запуск / эксплуатация

Для Hayden эта часть ключевая, поэтому подробный разбор вынесен также в отдельный раздел ниже.

Быстрый запуск:

```bash
docker compose up -d --build
```

Логи:

```bash
docker compose logs -f
```

Миграции:

```bash
docker compose exec web python manage.py migrate
```

Суперпользователь:

```bash
docker compose exec web python manage.py createsuperuser
```

Статика:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Остановка:

```bash
docker compose down
```

# Docker, Deploy и SMTP

## Docker

### Какие сервисы есть в `docker-compose.yml`

В текущей версии проекта есть два сервиса:

| Сервис | Назначение |
|---|---|
| `web` | Django-приложение под Gunicorn |
| `nginx` | Reverse proxy, публичный HTTP-вход, раздача static/media |

### Какой сервис отвечает за Django

За Django отвечает сервис `web`.

Он:

- собирается из локального `Dockerfile`;
- читает переменные из `.env`;
- применяет миграции;
- собирает static;
- запускает Gunicorn;
- слушает внутренний порт 8000;
- использует volumes для persistent data.

Команда сервиса:

```yaml
command: >
  sh -c "python manage.py migrate &&
         python manage.py collectstatic --noinput &&
  gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --no-control-socket"
```

Опция `--no-control-socket` добавлена, чтобы избежать проблем с control socket Gunicorn в контейнерной среде.

### Какой сервис отвечает за БД

Отдельного сервиса БД в текущей версии проекта нет. PostgreSQL/MySQL контейнер не обнаружен.

База данных — SQLite-файл. Путь задаётся переменной:

```env
DJANGO_DB_PATH=/app/data/db.sqlite3
```

Файл хранится в Docker volume `sqlite_data`, поэтому данные не исчезают при пересборке образа.

### Какие volumes используются

| Volume | Путь в контейнере | Назначение |
|---|---|---|
| `sqlite_data` | `/app/data` | SQLite database |
| `static_data` | `/app/staticfiles` | Собранная статика |
| `media_data` | `/app/media` | Загруженные файлы, например avatar |
| `logs_data` | `/app/logs` | Логи приложения |
| `sent_emails_data` | `/app/sent_emails` | Письма filebased email backend |

### Какие ports проброшены

Внешний порт проброшен только у `nginx`:

```yaml
ports:
  - "80:80"
```

Сервис `web` имеет:

```yaml
expose:
  - "8000"
```

`expose` открывает порт внутри Docker network, но не публикует его наружу. Пользователь идёт на `http://server-ip/`, Nginx проксирует запрос в `web:8000`.

### Какие environment variables нужны

Основные переменные из `.env.example`:

```env
DJANGO_SECRET_KEY=change-this-secret-key-before-deploy
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=188.187.214.161,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://188.187.214.161
DJANGO_DB_PATH=/app/data/db.sqlite3
DJANGO_STATIC_ROOT=/app/staticfiles
DJANGO_MEDIA_ROOT=/app/media
DJANGO_EMAIL_FILE_PATH=/app/sent_emails
DJANGO_LOG_DIR=/app/logs
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.hosting.reg.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=no-reply@example.ru
EMAIL_HOST_PASSWORD=change-me
DEFAULT_FROM_EMAIL=no-reply@example.ru
SERVER_EMAIL=no-reply@example.ru
```

`DJANGO_SECRET_KEY` должен быть уникальным и секретным. `DJANGO_ALLOWED_HOSTS` должен включать домен или IP сервера. `DJANGO_CSRF_TRUSTED_ORIGINS` должен совпадать с публичным origin.

## Команды запуска

Сервис Django в текущем `docker-compose.yml` называется `web`, поэтому команды используют `web`.

Собрать и запустить:

```bash
docker compose up -d --build
```

Смотреть логи всех сервисов:

```bash
docker compose logs -f
```

Смотреть только Django:

```bash
docker compose logs -f web
```

Смотреть только Nginx:

```bash
docker compose logs -f nginx
```

Применить миграции:

```bash
docker compose exec web python manage.py migrate
```

Создать суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

Собрать статику:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Остановить проект:

```bash
docker compose down
```

Полная типовая последовательность деплоя:

```bash
git pull
docker compose up -d --build
docker compose logs -f web
```

Если обновились только templates/static, всё равно безопасно запускать `up -d --build`: сервис `web` при старте выполнит миграции и collectstatic.

## SMTP

### Где находятся SMTP-настройки

SMTP-настройки читаются в `config/settings.py`:

```python
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() in ("true", "1", "yes", "on")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes", "on")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "webmaster@localhost")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
```

Пример значений находится в `.env.example`.

### Какие переменные окружения используются

- `EMAIL_BACKEND`;
- `EMAIL_HOST`;
- `EMAIL_PORT`;
- `EMAIL_USE_TLS`;
- `EMAIL_USE_SSL`;
- `EMAIL_HOST_USER`;
- `EMAIL_HOST_PASSWORD`;
- `DEFAULT_FROM_EMAIL`;
- `SERVER_EMAIL`;
- `DJANGO_EMAIL_FILE_PATH`.

### Для чего SMTP нужен проекту

SMTP нужен для отправки писем восстановления пароля через стандартные Django auth views. Пользователь открывает `/auth/password_reset/`, вводит email, Django формирует письмо и передаёт его email backend.

Если `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, письмо отправляется через SMTP-сервер. Если используется filebased backend, письмо сохраняется в директорию `sent_emails/`.

### Как проверить отправку писем

Вариант 1: через password reset UI:

1. Открыть `/auth/password_reset/`.
2. Ввести email существующего пользователя.
3. Проверить почтовый ящик.
4. Если backend filebased, проверить `sent_emails/` или Docker volume `sent_emails_data`.

Вариант 2: через Django command:

```bash
docker compose exec web python manage.py sendtestemail user@example.com
```

Локально:

```bash
python manage.py sendtestemail user@example.com
```

### Что делать, если письмо попало в спам

Проверить:

- совпадает ли `DEFAULT_FROM_EMAIL` с реальным доменом отправителя;
- настроены ли SPF/DKIM/DMARC у домена;
- не выглядит ли тема/тело письма подозрительно;
- не используется ли бесплатный/тестовый SMTP без репутации;
- не отправляется ли много писем подряд.

### Что делать, если SMTP не работает

Проверить `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...
```

Проверить логи:

```bash
docker compose logs -f web
```

Проверить сетевую доступность SMTP из контейнера:

```bash
docker compose exec web python manage.py shell
```

В shell можно вызвать `django.core.mail.send_mail`. Отдельной пользовательской страницы проверки SMTP в текущей версии проекта не обнаружено; проверка должна выполняться через password reset flow или `sendtestemail`.

## 13. Команды для проверки работы

Локально:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py runserver
python -m pytest tests/test_habits.py
python -m pytest
```

В текущем окружении без системной команды `python`:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest
```

Docker:

```bash
docker compose up -d --build
docker compose logs -f
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
docker compose down
```

Ручная проверка:

```text
/habits/
/habits/create/
/habits/<pk>/
/habits/<pk>/edit/
/habits/<pk>/delete/
/habits/<pk>/complete/
```

## 14. Возможные проблемы и способы решения

### Миграции не применяются

Проверить:

```bash
python manage.py showmigrations
python manage.py migrate
```

В Docker:

```bash
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py migrate
```

### Пользователь не видит привычки

Проверить, что пользователь авторизован и привычки созданы именно для него. Список использует `request.user.habits.all()`, чужие привычки не отображаются.

### Ошибка доступа к чужой привычке

Это ожидаемое поведение. `OwnerHabitQuerysetMixin` возвращает 404 и пишет warning. Нужно открыть привычку владельцем.

### Не создаётся выполнение

Проверить:

- запрос должен быть POST;
- пользователь должен быть владельцем привычки;
- выполнение за текущую дату не должно уже существовать.

Если уже существует, `get_or_create` не создаст дубль.

### Форма привычки не сохраняется

Проверить:

- title минимум 3 символа;
- target_count от 1 до 30;
- для daily target_count не больше 7;
- color в формате `#RRGGBB`;
- inactive habit должен иметь description;
- текст не содержит запрещённые слова.

### Docker container не стартует

Проверить:

```bash
docker compose logs -f web
docker compose logs -f nginx
```

Типичные причины:

- нет `.env`;
- неправильный `DJANGO_SECRET_KEY`;
- `DJANGO_ALLOWED_HOSTS` не содержит IP/домен;
- ошибка миграций;
- порт 80 уже занят.

### Nginx отдаёт 502

Проверить, запущен ли `web`:

```bash
docker compose ps
docker compose logs -f web
```

Если Gunicorn не стартовал, Nginx не сможет проксировать запросы.

### SMTP не отправляет письма

Проверить переменные EMAIL, пароль приложения, TLS/SSL, порт и логи Django. Для проверки использовать `/auth/password_reset/` или `sendtestemail`.

### README устарел

Сравнить README с текущими файлами:

```bash
find . -maxdepth 3 -type f | sort
```

После изменения маршрутов, Docker или settings нужно обновить README.

## 15. Что можно улучшить

- Слить и стабилизировать DRF REST API из ветки `feature/rest-api`.
- Добавить Swagger/OpenAPI в основную ветку.
- Добавить календарь привычек.
- Добавить streaks и серию успешных дней.
- Добавить email reminders о привычках.
- Добавить Celery и периодические задачи.
- Добавить PostgreSQL-сервис в Docker Compose для production.
- Добавить HTTPS и доменное имя.
- Добавить CI/CD pipeline.
- Покрыть validators и forms отдельными unit-тестами.
- Добавить backup/restore для SQLite volume.
- Улучшить README разделом troubleshooting по production.

## 16. Итоговый вклад участника

Hayden2572 реализовал ядро Habit Tracker: модели Habit и HabitCompletion, формы, валидаторы, CRUD views, защиту доступа к чужим привычкам, шаблоны привычек, логирование действий, README и контейнеризацию проекта через Docker Compose, Gunicorn и Nginx. Его вклад превращает базовый Django-проект в полноценный пользовательский трекер привычек, который можно запускать локально и деплоить на сервер.
