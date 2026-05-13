# Трекер привычек

Трекер привычек — это Django-приложение, в котором пользователь может зарегистрироваться, войти в аккаунт, создавать привычки, редактировать их, удалять, отмечать выполнение за текущий день и смотреть аналитику по прогрессу.

Проект построен как классическое Django-приложение с разделением на модули:

- `core` — главная страница;
- `users` — регистрация, кастомный пользователь, профильные поля;
- `habits` — привычки, выполнения привычек, CRUD и формы;
- `analytics` — статистика, графики и JSON API;
- `config` — настройки проекта и корневая маршрутизация.

## Стек

- Python 3;
- Django;
- SQLite;
- Bootstrap 5 через CDN;
- Matplotlib для построения графиков;
- Requests для получения внешней мотивирующей цитаты;
- Pillow для изображений профиля;
- Pytest и pytest-django для тестов.

## Как запустить проект

1. Создать виртуальное окружение:

```bash
python3 -m venv .venv
```

2. Активировать окружение.

Для bash/zsh:

```bash
source .venv/bin/activate
```

Для fish shell:

```fish
source .venv/bin/activate.fish
```

Для Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
```

3. Установить зависимости:

```bash
python -m pip install -r requirements.txt
```

4. Применить миграции:

```bash
python manage.py migrate
```

5. При необходимости создать администратора:

```bash
python manage.py createsuperuser
```

6. Запустить сервер:

```bash
python manage.py runserver
```

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Деплой на сервер через Docker Compose

Для сервера `188.187.214.161` и пользователя `mark` в проект добавлены:

- `Dockerfile` — собирает контейнер Django-приложения;
- `docker-compose.yml` — запускает Django через Gunicorn и Nginx на 80 порту;
- `deploy/nginx.conf` — конфиг Nginx;
- `.env.example` — пример production-переменных окружения;
- `.dockerignore` — исключает из Docker build лишние локальные файлы.

Схема запуска:

```text
Браузер -> http://188.187.214.161 -> Nginx:80 -> Gunicorn:8000 -> Django
```

SQLite-база, медиа, статика, логи и письма лежат в Docker volumes:

- `sqlite_data` — база `/app/data/db.sqlite3`;
- `media_data` — загруженные файлы `/app/media`;
- `static_data` — собранная статика `/app/staticfiles`;
- `logs_data` — логи `/app/logs`;
- `sent_emails_data` — письма восстановления пароля `/app/sent_emails`.

### 1. Зайти на сервер

```bash
ssh mark@188.187.214.161
```

### 2. Установить Docker и Compose plugin

Для Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker mark
```

После добавления пользователя в группу `docker` нужно перелогиниться:

```bash
exit
ssh mark@188.187.214.161
```

Проверка:

```bash
docker --version
docker compose version
```

Если на сервере включён `ufw`, открыть HTTP-порт:

```bash
sudo ufw allow 80/tcp
sudo ufw status
```

### 3. Перенести проект на сервер

Вариант через Git:

```bash
cd /home/mark
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> habit-tracker
cd habit-tracker
```

Если репозитория на сервере нет, можно отправить текущую папку с локальной машины:

```bash
rsync -av \
  --exclude .git \
  --exclude .venv \
  --exclude db.sqlite3 \
  --exclude media \
  --exclude logs \
  ./ mark@188.187.214.161:/home/mark/habit-tracker/
```

Потом зайти на сервер:

```bash
ssh mark@188.187.214.161
cd /home/mark/habit-tracker
```

### 4. Создать `.env`

На сервере:

```bash
cp .env.example .env
nano .env
```

Пример содержимого:

```env
DJANGO_SECRET_KEY=deploy
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=188.187.214.161,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://188.187.214.161
DJANGO_DB_PATH=/app/data/db.sqlite3
DJANGO_STATIC_ROOT=/app/staticfiles
DJANGO_MEDIA_ROOT=/app/media
DJANGO_EMAIL_FILE_PATH=/app/sent_emails
DJANGO_LOG_DIR=/app/logs
```

`DJANGO_SECRET_KEY` нужно заменить. Можно сгенерировать так:

```bash
openssl rand -hex 32
```

И вставить результат:

```env
DJANGO_SECRET_KEY=сюда_вставить_сгенерированную_строку
```

### 5. Собрать и запустить контейнеры

```bash
docker compose up -d --build
```

Что произойдёт при запуске:

1. Соберётся образ Django-приложения.
2. Контейнер `web` применит миграции: `python manage.py migrate`.
3. Контейнер `web` соберёт статику: `python manage.py collectstatic --noinput`.
4. Django запустится через Gunicorn на внутреннем порту `8000`.
5. Nginx откроет внешний порт `80` и проксирует запросы в `web`.

Проверить статус:

```bash
docker compose ps
```

Посмотреть логи:

```bash
docker compose logs -f
```

Открыть приложение:

```text
http://188.187.214.161/
```

### 6. Создать администратора

```bash
docker compose exec web python manage.py createsuperuser
```

Админка будет доступна здесь:

```text
http://188.187.214.161/admin/
```

### 7. Полезные команды на сервере

Остановить проект:

```bash
docker compose down
```

Запустить снова:

```bash
docker compose up -d
```

Пересобрать после изменения кода:

```bash
docker compose up -d --build
```

Применить миграции вручную:

```bash
docker compose exec web python manage.py migrate
```

Собрать статику вручную:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Открыть Django shell:

```bash
docker compose exec web python manage.py shell
```

Посмотреть последние логи:

```bash
docker compose logs --tail=100 web
docker compose logs --tail=100 nginx
```

### 8. Обновление проекта на сервере

Если проект был загружен через Git:

```bash
cd /home/mark/habit-tracker
git pull
docker compose up -d --build
```

Если проект отправляется через `rsync`, повторить отправку с локальной машины, затем на сервере:

```bash
cd /home/mark/habit-tracker
docker compose up -d --build
```

### 9. Важные замечания для защиты

- На сервере проект работает не через `runserver`, а через Gunicorn.
- Nginx принимает HTTP-запросы на 80 порту и отдаёт `/static/` и `/media/`.
- `DEBUG=False`, поэтому Django работает в production-режиме.
- IP `188.187.214.161` указан в `DJANGO_ALLOWED_HOSTS`, иначе Django вернул бы `DisallowedHost`.
- CSRF origin `http://188.187.214.161` указан в `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Данные не пропадают при пересборке, потому что база SQLite и media лежат в Docker volumes.
- Для реального публичного проекта лучше добавить домен, HTTPS-сертификат и заменить SQLite на PostgreSQL, но для учебного деплоя текущей схемы достаточно.

## Основные настройки проекта

Файл настроек: `config/settings.py`.

Важные параметры:

- `INSTALLED_APPS` подключает `core`, `users`, `habits`, `analytics`;
- `AUTH_USER_MODEL = "users.CustomUser"` задаёт кастомную модель пользователя;
- `LOGIN_URL = "login"` отправляет неавторизованных пользователей на страницу входа;
- `LOGIN_REDIRECT_URL = "habit_list"` после входа ведёт на список привычек;
- `LOGOUT_REDIRECT_URL = "home"` после выхода ведёт на главную;
- `EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"` сохраняет письма восстановления пароля в файлы;
- `EMAIL_FILE_PATH = BASE_DIR / "sent_emails"` указывает папку для этих писем;
- `LOGGING` пишет логи в консоль и файлы `logs/app.log`, `logs/daily.log`;
- база данных по умолчанию — SQLite-файл `db.sqlite3`.

## Структура файлов

```text
config/
  settings.py      настройки Django, база, auth, email, logging
  urls.py          корневые URL проекта
  asgi.py          ASGI-вход
  wsgi.py          WSGI-вход

core/
  views.py         главная страница
  urls.py          URL главной страницы
  templatetags/
    form_tags.py   фильтр add_class для добавления CSS-классов полям формы

users/
  models.py        CustomUser
  forms.py         форма регистрации CustomUserCreationForm
  views.py         регистрация и редирект после неё
  urls.py          URL регистрации
  admin.py         настройка пользователя в админке
  signals.py       логирование входа и неудачных попыток входа

habits/
  models.py        Habit и HabitCompletion
  forms.py         HabitForm и HabitCompletionForm
  views.py         CRUD привычек и отметка выполнения
  urls.py          URL привычек
  validators.py    валидация названия, цвета, цели, запрещённых слов
  admin.py         отображение привычек в админке

analytics/
  services.py      расчёт статистики
  charts.py        построение графиков Matplotlib
  external_api.py  мотивирующая цитата
  views.py         dashboard и JSON API
  urls.py          URL аналитики

templates/
  base.html                         общий layout
  core/home.html                    главная
  users/register.html               регистрация
  habits/habit_list.html            список привычек
  habits/habit_detail.html          карточка привычки и отметка выполнения
  habits/habit_form.html            создание и редактирование привычки
  habits/habit_confirm_delete.html  подтверждение удаления
  analytics/dashboard.html          аналитика
  registration/*.html               стандартные страницы auth Django

tests/
  conftest.py                фикстуры пользователя, привычки и клиента
  test_users.py             тесты регистрации, входа, выхода, смены пароля
  test_habits.py            тесты CRUD и выполнения привычек
  test_analytics.py         тесты аналитики и JSON API
  test_regex_validators.py  тесты regex-утилит
```

## Корневая маршрутизация

Корневые URL задаются в `config/urls.py`.

| URL | Подключаемый файл | За что отвечает |
| --- | --- | --- |
| `/admin/` | `django.contrib.admin.site.urls` | Админка Django |
| `/` | `core.urls` | Главная страница |
| `/auth/` | `django.contrib.auth.urls` | Вход, выход, смена и восстановление пароля |
| `/auth/` | `users.urls` | Регистрация |
| `/habits/` | `habits.urls` | CRUD привычек и отметка выполнения |
| `/analytics/` | `analytics.urls` | Аналитика и API статистики |

Важно: два подключения начинаются с `/auth/`. Это нормально: стандартные auth-URL Django дают `/auth/login/`, `/auth/logout/`, `/auth/password_change/` и другие, а `users.urls` добавляет `/auth/register/`.

## URL-ы приложения

### Core

Файл: `core/urls.py`.

| URL | name | View | Template | Что делает |
| --- | --- | --- | --- | --- |
| `/` | `home` | `core.views.home` | `templates/core/home.html` | Показывает главную страницу |

`core.views.home` просто вызывает `render(request, "core/home.html")`.

### Users и авторизация

Файл пользовательской регистрации: `users/urls.py`.

| URL | name | View | Template | Редирект |
| --- | --- | --- | --- | --- |
| `/auth/register/` | `register` | `users.views.register` | `templates/users/register.html` | После успешной регистрации на `habit_list`, если маршрут есть; иначе на `home` |

Стандартные URL Django подключены через `django.contrib.auth.urls` в `config/urls.py`.

| URL | name | Template | Редирект |
| --- | --- | --- | --- |
| `/auth/login/` | `login` | `templates/registration/login.html` | После входа на `habit_list`, потому что в `settings.py` задан `LOGIN_REDIRECT_URL` |
| `/auth/logout/` | `logout` | `templates/registration/logged_out.html` | После выхода на `home`, потому что задан `LOGOUT_REDIRECT_URL` |
| `/auth/password_change/` | `password_change` | `templates/registration/password_change_form.html` | После смены пароля на `password_change_done` |
| `/auth/password_change/done/` | `password_change_done` | `templates/registration/password_change_done.html` | Показывает сообщение об успешной смене |
| `/auth/password_reset/` | `password_reset` | `templates/registration/password_reset_form.html` | После отправки формы на `password_reset_done` |
| `/auth/password_reset/done/` | `password_reset_done` | `templates/registration/password_reset_done.html` | Сообщает, что письмо отправлено |
| `/auth/reset/<uidb64>/<token>/` | `password_reset_confirm` | `templates/registration/password_reset_confirm.html` | После сохранения нового пароля на `password_reset_complete` |
| `/auth/reset/done/` | `password_reset_complete` | `templates/registration/password_reset_complete.html` | Показывает финальное сообщение |

Письмо восстановления пароля формируется шаблонами:

- `templates/registration/password_reset_email.html`;
- `templates/registration/password_reset_subject.txt`.

Так как используется файловый email backend, письмо не отправляется наружу, а сохраняется в `sent_emails/`.

### Habits

Файл: `habits/urls.py`.

| URL | name | View | Template | Доступ |
| --- | --- | --- | --- | --- |
| `/habits/` | `habit_list` | `HabitListView` | `templates/habits/habit_list.html` | Только авторизованным |
| `/habits/create/` | `habit_create` | `HabitCreateView` | `templates/habits/habit_form.html` | Только авторизованным |
| `/habits/<pk>/` | `habit_detail` | `HabitDetailView` | `templates/habits/habit_detail.html` | Только владелец привычки |
| `/habits/<pk>/edit/` | `habit_update` | `HabitUpdateView` | `templates/habits/habit_form.html` | Только владелец привычки |
| `/habits/<pk>/delete/` | `habit_delete` | `HabitDeleteView` | `templates/habits/habit_confirm_delete.html` | Только владелец привычки |
| `/habits/<pk>/complete/` | `habit_complete` | function view | Без отдельного шаблона | Только владелец привычки, только POST |

Неавторизованный пользователь при попытке открыть URL из `habits` получает редирект на `/auth/login/`.

Если пользователь пытается открыть чужую привычку, `OwnerHabitQuerysetMixin` в `habits/views.py` возвращает `Http404("Привычка не найдена.")`. Так приложение не раскрывает, существует ли чужая запись.

### Analytics

Файл: `analytics/urls.py`.

| URL | name | View | Template/ответ | Доступ |
| --- | --- | --- | --- | --- |
| `/analytics/` | `analytics_dashboard` | `analytics.views.dashboard` | `templates/analytics/dashboard.html` | Только авторизованным |
| `/analytics/api/stats/` | `analytics_api_stats` | `analytics.views.api_stats` | JSON | Только авторизованным |

Неавторизованный пользователь редиректится на `/auth/login/`.

## CRUD привычек

CRUD реализован в приложении `habits`.

Основные файлы:

- `habits/models.py` — модели `Habit` и `HabitCompletion`;
- `habits/forms.py` — формы `HabitForm` и `HabitCompletionForm`;
- `habits/views.py` — классы и функции для CRUD;
- `habits/urls.py` — маршруты;
- `templates/habits/*.html` — страницы интерфейса.

### Create: создание привычки

URL:

```text
GET  /habits/create/
POST /habits/create/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("create/", HabitCreateView.as_view(), name="habit_create")`;
- view: `HabitCreateView` в `habits/views.py`;
- form: `HabitForm` в `habits/forms.py`;
- template: `templates/habits/habit_form.html`;
- model: `Habit` в `habits/models.py`.

Как работает:

1. Пользователь открывает `/habits/create/`.
2. `HabitCreateView` показывает форму `HabitForm`.
3. Пользователь отправляет POST.
4. В `form_valid` привычке присваивается текущий пользователь: `form.instance.user = self.request.user`.
5. Django сохраняет объект `Habit`.
6. Редирект идёт на `get_absolute_url()` модели `Habit`.
7. `Habit.get_absolute_url()` возвращает `reverse("habit_detail", kwargs={"pk": self.pk})`.
8. Итоговый редирект: `/habits/<pk>/`.

Поля формы:

- `title` — название;
- `description` — описание;
- `frequency` — ежедневная, еженедельная или ежемесячная;
- `target_count` — целевое количество;
- `color` — цвет в формате `#RRGGBB`;
- `is_active` — активность привычки.

### Read: просмотр списка привычек

URL:

```text
GET /habits/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("", HabitListView.as_view(), name="habit_list")`;
- view: `HabitListView` в `habits/views.py`;
- template: `templates/habits/habit_list.html`;
- model: `Habit`.

Как работает:

1. Пользователь открывает `/habits/`.
2. `HabitListView.get_queryset()` возвращает только привычки текущего пользователя: `self.request.user.habits.all()`.
3. Шаблон получает список в переменной `habits`.
4. В интерфейсе доступны кнопки `Подробнее`, `Редактировать`, `Удалить`, `Добавить привычку`.

Если привычек нет, шаблон показывает сообщение и кнопку создания первой привычки.

### Read: просмотр одной привычки

URL:

```text
GET /habits/<pk>/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("<int:pk>/", HabitDetailView.as_view(), name="habit_detail")`;
- view: `HabitDetailView` в `habits/views.py`;
- template: `templates/habits/habit_detail.html`;
- form: `HabitCompletionForm` для отметки выполнения;
- model: `Habit`, `HabitCompletion`.

Как работает:

1. Пользователь открывает `/habits/<pk>/`.
2. `OwnerHabitQuerysetMixin.get_object()` проверяет, что привычка принадлежит текущему пользователю.
3. Если привычка чужая или не существует, возвращается 404.
4. Шаблон показывает данные привычки, форму отметки выполнения и историю выполнений.
5. Форма отметки выполнения сейчас содержит только поле `note`; дату пользователь не вводит.

История выполнений берётся через related name `object.completions.all`, который задан в модели `HabitCompletion`.

### Update: редактирование привычки

URL:

```text
GET  /habits/<pk>/edit/
POST /habits/<pk>/edit/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("<int:pk>/edit/", HabitUpdateView.as_view(), name="habit_update")`;
- view: `HabitUpdateView` в `habits/views.py`;
- form: `HabitForm`;
- template: `templates/habits/habit_form.html`;
- model: `Habit`.

Как работает:

1. Пользователь открывает страницу редактирования.
2. `OwnerHabitQuerysetMixin` проверяет владельца привычки.
3. `HabitUpdateView` показывает форму с текущими значениями.
4. После POST валидная форма сохраняет изменения.
5. Редирект снова идёт через `Habit.get_absolute_url()`.
6. Итоговый редирект: `/habits/<pk>/`.

### Delete: удаление привычки

URL:

```text
GET  /habits/<pk>/delete/
POST /habits/<pk>/delete/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete")`;
- view: `HabitDeleteView` в `habits/views.py`;
- template: `templates/habits/habit_confirm_delete.html`;
- model: `Habit`.

Как работает:

1. Пользователь открывает страницу удаления.
2. `OwnerHabitQuerysetMixin` проверяет владельца.
3. Шаблон показывает подтверждение удаления.
4. После POST объект удаляется.
5. Редирект задан явно: `success_url = reverse_lazy("habit_list")`.
6. Итоговый редирект: `/habits/`.

### Дополнительное действие: отметка выполнения

Это не классический CRUD для привычки, а отдельное действие над привычкой.

URL:

```text
POST /habits/<pk>/complete/
```

Файлы:

- URL: `habits/urls.py`, маршрут `path("<int:pk>/complete/", habit_complete, name="habit_complete")`;
- view: `habit_complete` в `habits/views.py`;
- form: `HabitCompletionForm` в `habits/forms.py`;
- template с формой: `templates/habits/habit_detail.html`;
- model: `HabitCompletion`.

Как работает:

1. Пользователь нажимает `Отметить выполненной сегодня` на странице `/habits/<pk>/`.
2. Форма отправляет POST на `/habits/<pk>/complete/`.
3. `@login_required` требует авторизацию.
4. `@require_POST` запрещает GET-запросы к этому действию.
5. View проверяет, что привычка принадлежит пользователю.
6. Берётся заметка из `request.POST.get("note", "").strip()`.
7. Дата выполнения ставится автоматически: `completed_at=timezone.localdate()`.
8. `HabitCompletion.objects.get_or_create(...)` создаёт запись только если за сегодня её ещё нет.
9. Если запись за сегодня уже есть, дубль не создаётся.
10. Итоговый редирект всегда обратно на `habit_detail`: `/habits/<pk>/`.

Ограничение от дублей задано также на уровне модели:

```python
unique_together = ["habit", "completed_at"]
```

## Модели

### `CustomUser`

Файл: `users/models.py`.

Расширяет стандартного `AbstractUser`.

Дополнительные поля:

- `email` — уникальная электронная почта;
- `avatar` — изображение профиля;
- `bio` — описание пользователя;
- `phone` — телефон;
- `created_at` — дата регистрации.

### `Habit`

Файл: `habits/models.py`.

Поля:

- `user` — владелец привычки;
- `title` — название;
- `description` — описание;
- `frequency` — периодичность: `daily`, `weekly`, `monthly`;
- `target_count` — целевое количество;
- `color` — цвет;
- `is_active` — активна ли привычка;
- `created_at` — дата создания;
- `updated_at` — дата обновления.

Важный метод:

```python
def get_absolute_url(self):
    return reverse("habit_detail", kwargs={"pk": self.pk})
```

Этот метод используется после создания и редактирования привычки.

### `HabitCompletion`

Файл: `habits/models.py`.

Поля:

- `habit` — связь с привычкой;
- `completed_at` — дата выполнения;
- `note` — заметка;
- `created_at` — дата создания записи.

В модели задано ограничение:

```python
unique_together = ["habit", "completed_at"]
```

То есть одну и ту же привычку нельзя отметить выполненной два раза за одну дату.

## Формы и валидация

### `HabitForm`

Файл: `habits/forms.py`.

Используется для создания и редактирования привычки.

Поля:

- `title`;
- `description`;
- `frequency`;
- `target_count`;
- `color`;
- `is_active`.

Валидация:

- `clean_title()` проверяет длину названия и запрещённые слова;
- `clean_target_count()` проверяет диапазон от 1 до 30;
- `clean_color()` проверяет формат цвета `#RRGGBB`;
- `clean_description()` проверяет запрещённые слова;
- `clean()` дополнительно запрещает для ежедневной привычки цель больше 7 и требует описание для неактивной привычки.

Валидаторы находятся в `habits/validators.py`.

### `HabitCompletionForm`

Файл: `habits/forms.py`.

Используется на странице детали привычки для отметки выполнения.

Содержит только поле:

- `note` — короткая заметка.

Дата выполнения не вводится пользователем. Она выставляется в `habit_complete` автоматически через `timezone.localdate()`.

### `CustomUserCreationForm`

Файл: `users/forms.py`.

Используется на `/auth/register/`.

Поля:

- `username`;
- `email`;
- `phone`;
- `avatar`;
- `bio`;
- `password1`;
- `password2`.

Валидация:

- `clean_username()` требует минимум 5 символов;
- `clean_email()` требует обязательный email.

## Редиректы

| Действие | Где задано | Куда ведёт |
| --- | --- | --- |
| Успешный вход | `LOGIN_REDIRECT_URL` в `config/settings.py` | `habit_list`, то есть `/habits/` |
| Выход | `LOGOUT_REDIRECT_URL` в `config/settings.py` | `home`, то есть `/` |
| Регистрация | `_get_post_register_url()` в `users/views.py` | `habit_list`, если URL доступен; иначе `home` |
| Создание привычки | `Habit.get_absolute_url()` в `habits/models.py` | `habit_detail`, то есть `/habits/<pk>/` |
| Редактирование привычки | `Habit.get_absolute_url()` в `habits/models.py` | `habit_detail`, то есть `/habits/<pk>/` |
| Удаление привычки | `success_url = reverse_lazy("habit_list")` в `HabitDeleteView` | `/habits/` |
| Отметка выполнения | `redirect("habit_detail", pk=habit.pk)` в `habit_complete` | `/habits/<pk>/` |
| Неавторизованный доступ к habits/analytics | `LoginRequiredMixin` или `@login_required` | `/auth/login/?next=...` |
| Чужая привычка | `OwnerHabitQuerysetMixin` в `habits/views.py` | 404 |
| Смена пароля | стандартный Django auth URL | `password_change_done` |
| Восстановление пароля | стандартный Django auth URL | `password_reset_done`, затем `password_reset_complete` |

## Аналитика

Аналитика находится в приложении `analytics`.

### `analytics/services.py`

Содержит функции расчёта данных:

- `get_user_habit_stats(user)` возвращает общее количество привычек, активные привычки, количество выполнений, выполнено сегодня и список привычек;
- `get_completion_by_day(user, days=30)` возвращает количество выполнений по дням за период;
- `get_completed_vs_missed(user, days=30)` считает выполненные и пропущенные привычки.

### `analytics/charts.py`

Строит графики через Matplotlib и отдаёт их как base64-строки для вставки в HTML:

- `build_bar_chart()` — выполнения по привычкам;
- `build_pie_chart()` — выполнено и пропущено;
- `build_line_chart()` — выполнения по дням;
- `build_histogram()` — распределение выполнений;
- `build_scatter_chart()` — цель и факт выполнения.

Если данных нет, строится пустой график с поясняющим текстом.

### `analytics/views.py`

`dashboard(request)`:

1. Требует авторизацию через `@login_required`.
2. Собирает статистику через `get_user_habit_stats`.
3. Получает цитату через `get_motivational_quote`.
4. Создаёт графики.
5. Рендерит `templates/analytics/dashboard.html`.

`api_stats(request)`:

1. Требует авторизацию.
2. Возвращает JSON со статистикой текущего пользователя.
3. При ошибке возвращает JSON с `detail` и статусом 500.

## Защита проекта через Postman

Postman можно использовать на защите, чтобы показать, что URL-ы реально работают, авторизация защищает закрытые страницы, CRUD создаёт и меняет записи, а API аналитики отдаёт JSON.

Главная особенность проекта: это не token API, а обычное Django-приложение на session auth. Поэтому для POST-запросов нужны:

- cookie `csrftoken`;
- cookie `sessionid` после входа или регистрации;
- заголовок `X-CSRFToken` со значением CSRF-токена.

### Подготовка

1. Запустить сервер:

```bash
python manage.py runserver
```

1. В Postman создать Environment, например `Habit Tracker Local`.

2. Добавить переменные:

| Переменная | Значение |
| --- | --- |
| `base_url` | `http://127.0.0.1:8000` |
| `csrftoken` | пусто, заполнится после GET-запроса |
| `habit_id` | пусто, можно заполнить после создания привычки |
| `username` | например `postman_user` |
| `password` | например `StrongPass1!` |
| `email` | например `postman_user@example.com` |

Если пользователь с таким email уже существует, нужно поменять `username` и `email` или очистить тестовую базу.

### Как получить CSRF-токен

Перед любым POST-запросом нужно один раз открыть страницу, где Django выдаст cookie `csrftoken`.

Запрос:

```text
GET {{base_url}}/auth/login/
```

Ожидаемый результат:

- статус `200 OK`;
- в Cookies у домена `127.0.0.1` появляется `csrftoken`.

Чтобы не копировать токен руками, во вкладку `Tests` этого GET-запроса можно добавить:

```javascript
const csrf = pm.cookies.get("csrftoken");
if (csrf) {
  pm.environment.set("csrftoken", csrf);
}
```

После этого в POST-запросах добавляется header:

```text
X-CSRFToken: {{csrftoken}}
```

Postman сам будет хранить cookies в Cookie Jar. Если cookies не подставляются, нужно проверить, что включён Cookie Jar и запросы идут на один и тот же домен `127.0.0.1:8000`.

### Сценарий 1: показать защиту закрытого URL

Этот шаг удобно показывать первым: он доказывает, что привычки доступны только авторизованным пользователям.

Запрос:

```text
GET {{base_url}}/habits/
```

Если пользователь не авторизован, ожидаемый результат:

- статус `302 Found`, если в Postman выключен автоматический переход по redirect;
- header `Location` ведёт на `/auth/login/?next=/habits/`;
- если redirect включён, итогом будет HTML страницы входа.

Что говорить на защите:

```text
Список привычек закрыт LoginRequiredMixin. Неавторизованный пользователь не видит данные и отправляется на страницу входа.
```

То же самое можно показать для аналитики:

```text
GET {{base_url}}/analytics/
```

Ожидаемо будет redirect на login.

### Сценарий 2: регистрация пользователя

Сначала получить CSRF:

```text
GET {{base_url}}/auth/register/
```

Во вкладке `Tests` можно оставить тот же скрипт:

```javascript
const csrf = pm.cookies.get("csrftoken");
if (csrf) {
  pm.environment.set("csrftoken", csrf);
}
```

Затем отправить регистрацию.

Запрос:

```text
POST {{base_url}}/auth/register/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Body: `x-www-form-urlencoded`

| Key | Value |
| --- | --- |
| `username` | `{{username}}` |
| `email` | `{{email}}` |
| `phone` | `+79991234567` |
| `bio` | `Пользователь из Postman` |
| `password1` | `{{password}}` |
| `password2` | `{{password}}` |

Ожидаемый результат:

- статус `302 Found`;
- redirect на `/habits/`;
- появляется cookie `sessionid`;
- пользователь автоматически авторизован.

Что происходит в коде:

- URL описан в `users/urls.py`;
- запрос обрабатывает `users.views.register`;
- форма `CustomUserCreationForm` находится в `users/forms.py`;
- после `form.save()` вызывается `login(request, user)`;
- редирект выбирается функцией `_get_post_register_url()` и ведёт на `habit_list`.

Если хочется автоматически сохранить `sessionid`, во вкладку `Tests` можно добавить:

```javascript
const sessionid = pm.cookies.get("sessionid");
if (sessionid) {
  pm.environment.set("sessionid", sessionid);
}
```

Обычно руками использовать `sessionid` не нужно: Postman сам отправляет cookie дальше.

### Сценарий 3: вход существующего пользователя

Если пользователь уже создан, можно показать обычный login.

Сначала получить CSRF:

```text
GET {{base_url}}/auth/login/
```

Затем:

```text
POST {{base_url}}/auth/login/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Body: `x-www-form-urlencoded`

| Key | Value |
| --- | --- |
| `username` | `{{username}}` |
| `password` | `{{password}}` |

Ожидаемый результат:

- статус `302 Found`;
- redirect на `/habits/`;
- cookie `sessionid`.

Что говорить на защите:

```text
Django auth проверяет логин и пароль, создаёт sessionid, а LOGIN_REDIRECT_URL отправляет пользователя на список привычек.
```

### Сценарий 4: создание привычки через Postman

Запрос:

```text
POST {{base_url}}/habits/create/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Body: `x-www-form-urlencoded`

| Key | Value |
| --- | --- |
| `title` | `Читать документацию` |
| `description` | `20 минут вечером` |
| `frequency` | `daily` |
| `target_count` | `1` |
| `color` | `#4CAF50` |
| `is_active` | `on` |

Ожидаемый результат:

- статус `302 Found`;
- header `Location` похож на `/habits/1/`;
- привычка создаётся и привязывается к текущему пользователю.

Что происходит в коде:

- URL находится в `habits/urls.py`;
- view — `HabitCreateView`;
- форма — `HabitForm`;
- в `form_valid()` выполняется `form.instance.user = self.request.user`;
- после сохранения Django вызывает `Habit.get_absolute_url()`;
- редирект ведёт на detail созданной привычки.

Чтобы автоматически сохранить `habit_id` из redirect, во вкладку `Tests` можно добавить:

```javascript
const location = pm.response.headers.get("Location");
const match = location && location.match(/\/habits\/(\d+)\//);
if (match) {
  pm.environment.set("habit_id", match[1]);
}
```

Если в Postman включён автоматический redirect, статус может стать `200 OK`, потому что Postman сразу откроет страницу детали. Для демонстрации редиректа удобнее временно выключить `Automatically follow redirects`.

### Сценарий 5: просмотр списка и детали привычки

Список:

```text
GET {{base_url}}/habits/
```

Ожидаемый результат:

- статус `200 OK`;
- HTML содержит список привычек текущего пользователя.

Детальная страница:

```text
GET {{base_url}}/habits/{{habit_id}}/
```

Ожидаемый результат:

- статус `200 OK`;
- HTML содержит название, описание, цель, цвет, историю выполнений и форму отметки выполнения.

Что говорить на защите:

```text
HabitListView показывает только self.request.user.habits.all(), а HabitDetailView через OwnerHabitQuerysetMixin проверяет владельца записи.
```

### Сценарий 6: редактирование привычки

Запрос:

```text
POST {{base_url}}/habits/{{habit_id}}/edit/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Body: `x-www-form-urlencoded`

| Key | Value |
| --- | --- |
| `title` | `Читать документацию Django` |
| `description` | `30 минут вечером` |
| `frequency` | `weekly` |
| `target_count` | `3` |
| `color` | `#123456` |
| `is_active` | `on` |

Ожидаемый результат:

- статус `302 Found`;
- redirect на `/habits/{{habit_id}}/`;
- данные привычки обновлены.

Что происходит в коде:

- URL — `/habits/<pk>/edit/`;
- view — `HabitUpdateView`;
- проверка владельца — `OwnerHabitQuerysetMixin`;
- форма — `HabitForm`;
- редирект после сохранения идёт через `Habit.get_absolute_url()`.

### Сценарий 7: отметка выполнения

Запрос:

```text
POST {{base_url}}/habits/{{habit_id}}/complete/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Body: `x-www-form-urlencoded`

| Key | Value |
| --- | --- |
| `note` | `Выполнено через Postman` |

Ожидаемый результат:

- статус `302 Found`;
- redirect обратно на `/habits/{{habit_id}}/`;
- в истории появляется выполнение за сегодняшний день.

Что важно:

- дату выполнения пользователь не передаёт;
- дата ставится на сервере через `timezone.localdate()`;
- `get_or_create()` не создаёт дубль, если привычка уже отмечена сегодня;
- модель дополнительно защищена ограничением `unique_together = ["habit", "completed_at"]`.

Что говорить на защите:

```text
POST создаёт HabitCompletion только для текущего пользователя и только на текущую дату. Повторное нажатие за тот же день не создаёт вторую запись.
```

### Сценарий 8: JSON API аналитики

Запрос:

```text
GET {{base_url}}/analytics/api/stats/
```

Ожидаемый результат:

- статус `200 OK`;
- `Content-Type` начинается с `application/json`;
- тело содержит статистику текущего пользователя.

Пример ответа:

```json
{
  "total_habits": 1,
  "active_habits": 1,
  "total_completions": 1,
  "completed_today": 1,
  "habits": [
    {
      "id": 1,
      "title": "Читать документацию Django",
      "frequency": "weekly",
      "target_count": 3,
      "completion_count": 1,
      "last_completed": "2026-05-13"
    }
  ]
}
```

Что происходит в коде:

- URL находится в `analytics/urls.py`;
- view — `api_stats`;
- данные собирает `get_user_habit_stats()` из `analytics/services.py`;
- API защищён `@login_required`.

### Сценарий 9: проверка защиты чужой привычки

Для демонстрации можно создать второго пользователя, войти под ним и попробовать открыть привычку первого пользователя.

Пример:

```text
GET {{base_url}}/habits/{{habit_id}}/
```

Если `habit_id` принадлежит другому пользователю, ожидаемый результат:

- статус `404 Not Found`.

Что говорить на защите:

```text
Приложение не отдаёт чужие привычки. OwnerHabitQuerysetMixin сравнивает owner_id привычки с request.user.id и возвращает 404.
```

### Сценарий 10: выход

Запрос:

```text
POST {{base_url}}/auth/logout/
```

Headers:

```text
X-CSRFToken: {{csrftoken}}
```

Ожидаемый результат:

- статус `302 Found`;
- redirect на `/`;
- после выхода закрытые URL снова отправляют на login.

### Что показать комиссии в Postman коротко

Минимальный порядок демонстрации:

1. `GET /habits/` без входа — показать redirect на login.
2. `GET /auth/register/` — получить CSRF.
3. `POST /auth/register/` — создать пользователя и получить session.
4. `POST /habits/create/` — создать привычку.
5. `GET /habits/{{habit_id}}/` — показать detail.
6. `POST /habits/{{habit_id}}/complete/` — отметить выполнение.
7. `GET /analytics/api/stats/` — показать JSON-статистику.
8. `POST /auth/logout/` — выйти.
9. `GET /analytics/` после выхода — снова показать redirect на login.

Этого достаточно, чтобы защитить основные части проекта: авторизацию, CSRF, CRUD, принадлежность данных пользователю, отметку выполнения и аналитику.

## Тесты

Настройки pytest находятся в `pytest.ini`.

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

Запуск всех тестов:

```bash
pytest
```

Если используется виртуальное окружение проекта:

```bash
.venv/bin/python -m pytest
```

### `tests/conftest.py`

Общие фикстуры:

- `user` — основной пользователь;
- `another_user` — второй пользователь для проверки доступа к чужим данным;
- `authenticated_client` — Django test client с авторизованным пользователем;
- `habit` — тестовая привычка;
- `completed_habit` — выполненная привычка на сегодняшнюю дату.

### `tests/test_users.py`

Проверяет пользовательские сценарии:

- `test_successful_registration` — успешная регистрация, редирект на `habit_list`, создание пользователя и автоматический вход;
- `test_registration_validation_error` — ошибка регистрации при коротком имени и пустом email;
- `test_successful_login` — успешный вход и редирект на `habit_list`;
- `test_logout_redirect` — выход и редирект на `home`;
- `test_password_change_page_available_for_authenticated_user` — доступность страницы смены пароля для авторизованного пользователя.

### `tests/test_habits.py`

Проверяет привычки:

- `test_habit_list_requires_auth` — список привычек требует авторизацию;
- `test_create_habit` — создание привычки, привязка к пользователю и редирект на detail;
- `test_update_habit` — редактирование привычки и редирект на detail;
- `test_delete_habit` — удаление привычки и редирект на список;
- `test_user_cannot_access_another_users_habit` — чужая привычка возвращает 404;
- `test_complete_habit` — отметка выполнения создаёт `HabitCompletion` на сегодняшнюю дату;
- `test_duplicate_completion_for_same_day_is_not_created` — повторная отметка за тот же день не создаёт дубль.

### `tests/test_analytics.py`

Проверяет аналитику:

- `test_dashboard_requires_auth` — dashboard требует авторизацию;
- `test_dashboard_available_for_authenticated_user` — dashboard открывается авторизованному пользователю и получает статистику;
- `test_api_stats_returns_json` — API статистики возвращает JSON;
- `test_api_stats_contains_expected_keys` — JSON содержит ключи `total_habits`, `active_habits`, `total_completions`, `completed_today`, `habits`.

### `tests/test_regex_validators.py`

Проверяет вспомогательные regex-утилиты из `utils/validators.py`:

- `validate_login`;
- `find_dates`;
- `parse_log`;
- `validate_password`;
- `validate_email_domain`;
- `normalize_phone`.

## Условное распределение работы на 4 участников

Для командного отчёта проект можно представить как работу четырёх участников:

1. Участник 1 — пользователи и авторизация: `CustomUser`, форма регистрации, шаблоны входа, выхода, смены и восстановления пароля, интеграция с Django auth.
2. Участник 2 — привычки и CRUD: модели `Habit`, `HabitCompletion`, формы, валидаторы, CRUD-представления, URL-ы и шаблоны привычек.
3. Участник 3 — аналитика: сервисы статистики, графики Matplotlib, dashboard, JSON API и мотивирующая цитата.
4. Участник 4 — инфраструктура и качество: настройки проекта, маршрутизация, Bootstrap-интерфейс, русификация, логирование, pytest-конфигурация и тестовое покрытие.
