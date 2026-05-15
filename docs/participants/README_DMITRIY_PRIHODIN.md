# Отчёт участника: Dmitriy Prihodin

## 1. Общая информация

| Поле | Значение |
|---|---|
| ФИО / GitHub nickname | Dmitriy Prihodin |
| Email | d.prihodin816@gmail.com |
| Основная зона ответственности | Инициализация Django-проекта, приложения `users` и `core`, кастомная модель пользователя, регистрация, авторизация, auth templates, auth logging, email backend |
| Связанные ветки | `origin/feature/users-auth`, `feature/project-bootstrap`, `main` |
| Связанные Django-приложения | `core`, `users`, частично `config` |
| Связанные шаблоны | `templates/base.html`, `templates/core/home.html`, `templates/users/register.html`, `templates/registration/*.html` |
| Связанные тесты | `tests/test_users.py`, общие fixtures из `tests/conftest.py` |

Краткое описание вклада: участник заложил базовую структуру Django-проекта, подключил главную страницу, реализовал кастомную модель пользователя `users.CustomUser`, форму и view регистрации, подключил стандартную session-based авторизацию Django, подготовил auth templates, email backend для восстановления пароля и логирование событий входа/регистрации.

По истории Git вклад подтверждается коммитами:

```text
9f5f694 | Dmitriy Prihodin <d.prihodin816@gmail.com> | chore: initialize django project skeleton
caa3423 | Dmitriy Prihodin <d.prihodin816@gmail.com> | feat: create users and core apps
90d44c3 | Dmitriy Prihodin <d.prihodin816@gmail.com> | feat: implement custom user model
f721995 | Dmitriy Prihodin <d.prihodin816@gmail.com> | feat: add user registration flow
b7e9e33 | Dmitriy Prihodin <d.prihodin816@gmail.com> | feat: add auth templates and base layout
dc9c415 | Dmitriy Prihodin <d.prihodin816@gmail.com> | chore: configure auth logging and email backend
```

## 2. Краткое резюме выполненной работы

Dmitriy отвечал за фундамент приложения: Django project `config`, базовые приложения `core` и `users`, пользовательскую модель и пользовательские сценарии входа/регистрации. Эта часть нужна проекту, потому что трекер привычек персональный: привычки, выполнения и аналитика должны принадлежать конкретному пользователю. Без корректной модели пользователя, регистрации и авторизации невозможно безопасно отделить данные одного пользователя от данных другого.

В текущей архитектуре `users.CustomUser` является центральной моделью владельца данных. Приложение `habits` связывает `Habit.user` с `settings.AUTH_USER_MODEL`, а analytics собирает статистику через привычки текущего пользователя. Поэтому вклад Dmitriy является базовым слоем для всех последующих модулей.

Пользовательский интерфейс авторизации реализован через Django templates: главная страница, регистрация, вход, выход, восстановление и смена пароля. Session-based authentication Django сохраняет состояние входа в сессии, а `LoginRequiredMixin` и `login_required` в других приложениях используют этот слой для ограничения доступа.

В текущей версии проекта отдельная страница редактирования профиля пользователя не обнаружена. Профильные поля (`phone`, `avatar`, `bio`) есть в `users.CustomUser`, вывод и редактирование доступны через форму регистрации и Django admin. Если бы полноценная страница профиля реализовывалась, она логично находилась бы в `users/views.py`, `users/urls.py` и отдельном шаблоне в `templates/users/`.

## 3. Файлы и директории, относящиеся к работе участника

| Файл/папка | Назначение | Что реализовано |
|---|---|---|
| `manage.py` | CLI-вход Django | Запуск management-команд проекта |
| `config/settings.py` | Настройки проекта | `INSTALLED_APPS`, middleware, templates, SQLite, static/media, email backend, auth redirects, `AUTH_USER_MODEL`, logging |
| `config/urls.py` | Корневая маршрутизация | Подключение `/`, `/auth/`, `/habits/`, `/analytics/`, admin |
| `config/asgi.py` | ASGI-вход | Стандартная точка входа для ASGI-серверов |
| `config/wsgi.py` | WSGI-вход | Точка входа Gunicorn/Django |
| `core/apps.py` | Конфигурация приложения `core` | Django AppConfig |
| `core/views.py` | Главная страница | View `home`, который рендерит `templates/core/home.html` |
| `core/urls.py` | URL главной страницы | Маршрут `/` с именем `home` |
| `core/templatetags/form_tags.py` | Template filter | Фильтр `add_class` для CSS-классов полей форм |
| `users/apps.py` | Конфигурация приложения `users` | AppConfig и импорт `users.signals` в `ready()` |
| `users/models.py` | Пользовательская модель | `CustomUser` на базе `AbstractUser` с email, avatar, bio, phone, created_at |
| `users/forms.py` | Форма регистрации | `CustomUserCreationForm`, поля профиля, валидация username/email |
| `users/views.py` | Регистрация | View `register`, автоматический login, redirect, logging |
| `users/urls.py` | URL регистрации | `/auth/register/` |
| `users/signals.py` | Auth logging | Обработчики `user_logged_in` и `user_login_failed` |
| `users/admin.py` | Админка пользователя | Расширение `UserAdmin` дополнительными полями |
| `users/migrations/0001_initial.py` | Миграция модели пользователя | Создание `CustomUser` |
| `templates/base.html` | Общий layout | Навигация, auth-блок, messages, Bootstrap |
| `templates/core/home.html` | Главная страница | Стартовый экран и ссылки на регистрацию/вход |
| `templates/users/register.html` | Страница регистрации | HTML-форма регистрации с CSRF и ошибками |
| `templates/registration/login.html` | Страница входа | Стандартная форма login через Django auth |
| `templates/registration/logged_out.html` | Страница выхода | Экран после logout |
| `templates/registration/password_change_form.html` | Смена пароля | Форма смены пароля |
| `templates/registration/password_change_done.html` | Успешная смена пароля | Подтверждение результата |
| `templates/registration/password_reset_form.html` | Восстановление пароля | Форма ввода email |
| `templates/registration/password_reset_done.html` | Письмо отправлено | Информационный экран |
| `templates/registration/password_reset_email.html` | Email восстановления | Тело письма |
| `templates/registration/password_reset_subject.txt` | Тема письма | Subject письма восстановления |
| `templates/registration/password_reset_confirm.html` | Новый пароль | Форма подтверждения токена и нового пароля |
| `templates/registration/password_reset_complete.html` | Восстановление завершено | Финальный экран |
| `tests/test_users.py` | Тесты auth/users | Регистрация, ошибки регистрации, login, logout, password change |

## 4. Подробное описание реализации

### `config/settings.py`

Файл отвечает за конфигурацию Django-проекта. В нём подключены стандартные приложения Django (`admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`) и проектные приложения `core`, `users`, `habits`, `analytics`.

Ключевые настройки, связанные с зоной Dmitriy:

- `ROOT_URLCONF = "config.urls"` указывает корневой файл маршрутов.
- `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]` подключает общую директорию шаблонов.
- `AUTH_USER_MODEL = "users.CustomUser"` сообщает Django, что вместо стандартной модели `auth.User` используется пользовательская модель.
- `LOGIN_URL = "login"` задаёт route name страницы входа для `LoginRequiredMixin` и `login_required`.
- `LOGIN_REDIRECT_URL = "habit_list"` отправляет пользователя после входа к списку привычек.
- `LOGOUT_REDIRECT_URL = "home"` отправляет пользователя после выхода на главную страницу.
- `EMAIL_BACKEND`, `EMAIL_FILE_PATH`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL` задают почтовый backend.
- `LOGGING` настраивает запись логов в консоль и файлы.

Email backend по умолчанию файловый:

```python
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
```

Это удобно для учебного и локального проекта: письма восстановления пароля не уходят наружу, а сохраняются в директории `sent_emails/`. В production через `.env.example` можно переключить backend на SMTP.

### `config/urls.py`

Файл собирает корневую маршрутизацию проекта:

```text
/admin/      -> Django admin
/            -> core.urls
/auth/       -> django.contrib.auth.urls
/auth/       -> users.urls
/habits/     -> habits.urls
/analytics/  -> analytics.urls
```

Два подключения `/auth/` не конфликтуют. `django.contrib.auth.urls` даёт стандартные маршруты login/logout/password reset/password change, а `users.urls` добавляет регистрацию `/auth/register/`.

### `core/views.py`

Файл содержит функцию:

```python
def home(request):
    return render(request, "core/home.html")
```

Она принимает объект `request`, рендерит шаблон главной страницы и возвращает `HttpResponse`. Главная страница не требует авторизации и служит входной точкой для новых пользователей.

### `core/urls.py`

Маршрут:

```python
path("", home, name="home")
```

Он делает view `home` доступной по корневому URL `/`. Имя `home` используется в шаблонах и redirect-настройках, например `LOGOUT_REDIRECT_URL = "home"`.

### `core/templatetags/form_tags.py`

В текущей версии проекта файл реализует template filter `add_class`. Он нужен, чтобы в шаблонах добавлять Bootstrap-классы к Django form fields без ручного переписывания HTML каждого поля. Например в `templates/users/register.html` используется:

```django
{{ field|add_class:"form-control" }}
```

Это связывает backend-формы Django с Bootstrap-представлением.

### `users/models.py`

Файл содержит модель `CustomUser`, наследующуюся от `django.contrib.auth.models.AbstractUser`.

Реализованные поля:

- `email = models.EmailField(unique=True)` — уникальный email пользователя.
- `avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)` — необязательный аватар.
- `bio = models.TextField(blank=True)` — текст “о себе”.
- `phone = models.CharField(max_length=20, blank=True)` — телефон.
- `created_at = models.DateTimeField(auto_now_add=True)` — дата регистрации.

Метод `__str__()` возвращает `username`. Это удобно для админки, логов и связанных моделей: объект пользователя отображается читаемо.

`CustomUser` выбран вместо стандартного `User`, потому что проекту нужны профильные поля. В Django правильно делать такую замену в начале проекта, до активной разработки миграций, чтобы не усложнять связи.

### `users/forms.py`

Файл содержит `CustomUserCreationForm`, наследника стандартной `UserCreationForm`. Форма привязана к модели `CustomUser`.

Поля формы:

- `username`;
- `email`;
- `phone`;
- `avatar`;
- `bio`;
- `password1`;
- `password2`.

Форма добавляет labels, help texts и widgets. Это улучшает пользовательский интерфейс и помогает шаблону регистрации показывать понятные подписи.

Метод `clean_username()` проверяет, что имя пользователя содержит минимум 5 символов. Метод `clean_email()` проверяет обязательность email. Пароли проверяются стандартной логикой `UserCreationForm`: совпадение `password1`/`password2` и password validators из `AUTH_PASSWORD_VALIDATORS`.

### `users/views.py`

Файл реализует регистрацию пользователя.

Функция `_get_post_register_url()` пытается построить URL `habit_list`. Если приложение привычек ещё не подключено или route отсутствует, fallback ведёт на `home`. Такая защита была полезна на этапе поэтапной разработки проекта.

Функция `register(request)` работает так:

1. Если метод `POST`, создаётся `CustomUserCreationForm(request.POST, request.FILES)`.
2. Если форма валидна, вызывается `form.save()`, создаётся `CustomUser`.
3. Пользователь сразу авторизуется через `login(request, user)`.
4. Событие регистрации пишется в logger уровня `INFO`.
5. Выполняется redirect на список привычек или на главную.
6. Если форма невалидна, ошибки пишутся в logger уровня `WARNING`, а форма возвращается в шаблон.
7. Если метод `GET`, создаётся пустая форма.

Такой сценарий удобен для пользователя: после регистрации не нужно отдельно входить в аккаунт.

### `users/urls.py`

Файл добавляет маршрут регистрации:

```python
path("register/", register, name="register")
```

Так как в `config/urls.py` он подключён под `/auth/`, итоговый URL:

```text
/auth/register/
```

### `users/signals.py`

Файл подключает обработчики стандартных сигналов Django auth:

- `user_logged_in` — успешный вход пользователя;
- `user_login_failed` — неудачная попытка входа.

Функция `log_user_logged_in()` пишет `INFO`: какой пользователь вошёл. Функция `log_user_login_failed()` пишет `WARNING`: какой username пытался войти. Это важно для аудита безопасности и диагностики проблем авторизации.

### `users/apps.py`

`UsersConfig.ready()` импортирует `users.signals`, чтобы signal handlers зарегистрировались при старте приложения. Без этого файл `signals.py` мог бы не загрузиться, и auth-события не логировались бы.

### `users/admin.py`

Файл расширяет стандартную админку `UserAdmin`. В `fieldsets` добавлены `phone`, `avatar`, `bio`, `created_at`; в `add_fieldsets` добавлены поля, доступные при создании пользователя. `created_at` сделан readonly, потому что дата регистрации должна заполняться автоматически.

### `templates/base.html`

Это общий layout всего сайта. Он подключает Bootstrap 5, выводит навигацию, messages, auth-блок и footer.

Auth-блок работает от `user.is_authenticated`:

- для авторизованного пользователя показывает username, ссылку на смену пароля и POST-форму logout;
- для гостя показывает ссылки “Вход” и “Регистрация”.

Logout сделан POST-формой с CSRF-токеном. Это соответствует современному поведению Django, где logout не должен выполняться небезопасным GET-запросом.

### `templates/users/register.html`

Шаблон расширяет `base.html`, выводит форму регистрации, CSRF-токен, help texts, field errors и non-field errors. Для полей используется фильтр `add_class`, чтобы добавлять Bootstrap-класс `form-control`.

Форма имеет `enctype="multipart/form-data"`, потому что модель пользователя поддерживает загрузку avatar.

### `templates/registration/*.html`

В директории находятся шаблоны стандартных auth views Django:

- `login.html`;
- `logged_out.html`;
- `password_change_form.html`;
- `password_change_done.html`;
- `password_reset_form.html`;
- `password_reset_done.html`;
- `password_reset_email.html`;
- `password_reset_subject.txt`;
- `password_reset_confirm.html`;
- `password_reset_complete.html`.

Они позволяют использовать встроенные Django views без написания собственных классов для каждого auth-сценария. Django выбирает эти шаблоны по стандартным путям.

## 5. Теоретическая база

### Django project и Django app

Django project — это общая конфигурация сайта: settings, root urls, WSGI/ASGI. В этом проекте роль Django project выполняет директория `config/`.

Django app — отдельный модуль функциональности. В проекте есть приложения:

- `core` — главная страница;
- `users` — пользователи и регистрация;
- `habits` — привычки;
- `analytics` — аналитика.

Такое разделение помогает развивать проект по зонам ответственности и не смешивать unrelated-код.

### `settings.py` и `urls.py`

`settings.py` содержит настройки: установленные приложения, middleware, базу данных, templates, auth, email, logging, static/media.

`urls.py` описывает маршрутизацию: какой URL вызывает какой view или подключает какой набор URL. В `config/urls.py` собраны все приложения проекта.

### `CustomUser`

`CustomUser` — пользовательская модель пользователя. Она наследуется от `AbstractUser`, поэтому сохраняет стандартные поля Django (`username`, `password`, `is_staff`, `is_active`, `groups`, permissions), но добавляет проектные поля.

### Зачем нужен `AUTH_USER_MODEL`

`AUTH_USER_MODEL = "users.CustomUser"` нужен, чтобы весь проект ссылался на кастомную модель пользователя. Это особенно важно для `ForeignKey` в `habits.models.Habit`: связь идёт не с `auth.User`, а с актуальной моделью пользователя проекта.

### Регистрация и авторизация в Django

Регистрация в проекте выполняется через `CustomUserCreationForm` и view `register`. Авторизация использует стандартные views Django из `django.contrib.auth.urls`.

Django проверяет пароль, создаёт session key, сохраняет id пользователя в сессии и на следующих запросах восстанавливает `request.user`.

### Templates

Templates — HTML-файлы с Django Template Language. Они получают context от views и превращают данные в HTML. Например `register.html` получает `form`, а `base.html` использует `user.is_authenticated`.

### Session-based authentication

Session-based authentication хранит состояние входа на сервере в таблице/хранилище сессий, а браузеру выдаёт session cookie. Пользователь не передаёт логин и пароль на каждом запросе; Django определяет его по session id.

### Email backend

Email backend отвечает за отправку писем. В локальной версии используется filebased backend: письма сохраняются в файлы. В production можно включить SMTP backend через переменные окружения.

Email backend нужен для восстановления пароля: Django генерирует письмо со ссылкой на reset-confirm route.

### Логирование auth-событий

Логирование входа и ошибок входа нужно для:

- аудита действий пользователя;
- поиска проблем с авторизацией;
- обнаружения подозрительных попыток входа;
- отладки production-инцидентов.

## 6. Как это работает в проекте

### Сценарий регистрации

1. Пользователь открывает `/auth/register/`.
2. `users.urls` вызывает `users.views.register`.
3. View создаёт `CustomUserCreationForm`.
4. Шаблон `templates/users/register.html` показывает поля формы.
5. Пользователь отправляет POST.
6. Форма проверяет username, email, password1/password2 и стандартные password validators.
7. При успехе создаётся `CustomUser`.
8. View вызывает `login(request, user)`.
9. В session сохраняется id пользователя.
10. В лог пишется успешная регистрация.
11. Пользователь перенаправляется на `/habits/`.

### Сценарий входа

1. Пользователь открывает `/auth/login/`.
2. URL обслуживается стандартной Django auth view.
3. Django использует шаблон `templates/registration/login.html`.
4. Пользователь отправляет username/password.
5. Django проверяет credentials.
6. При успехе срабатывает signal `user_logged_in`.
7. `users.signals.log_user_logged_in()` пишет `INFO`.
8. Пользователь перенаправляется на `LOGIN_REDIRECT_URL`, то есть `/habits/`.

### Сценарий восстановления пароля

1. Пользователь открывает `/auth/password_reset/`.
2. Django показывает `password_reset_form.html`.
3. Пользователь вводит email.
4. Django формирует письмо из `password_reset_email.html` и `password_reset_subject.txt`.
5. В локальном режиме письмо сохраняется в `sent_emails/`.
6. Пользователь переходит по ссылке reset confirm.
7. Django показывает форму нового пароля.
8. После сохранения пользователь видит `password_reset_complete.html`.

## 7. Безопасность и ограничения доступа

В зоне Dmitriy реализован базовый auth-слой:

- стандартные Django session cookies;
- CSRF-токены в формах регистрации, login, logout, password reset/change;
- password validators в `AUTH_PASSWORD_VALIDATORS`;
- `AUTH_USER_MODEL`, чтобы все связи использовали единую модель пользователя;
- POST logout вместо GET logout;
- логирование успешных и неуспешных входов.

Страницы `/habits/` и `/analytics/` требуют авторизации уже в соответствующих приложениях через `LoginRequiredMixin` и `login_required`, но опираются именно на слой session auth из `users`.

Доступ к чужим привычкам реализован в `habits.views.OwnerHabitQuerysetMixin`, а не в `users`. Однако он использует `request.user`, который появляется благодаря auth middleware и session authentication.

Оставшиеся риски:

- в production нужно обязательно задать сильный `DJANGO_SECRET_KEY`;
- нужен HTTPS, иначе session cookie и password reset links могут быть перехвачены;
- SMTP credentials должны храниться только в `.env`, не в Git;
- можно добавить rate limiting для login/password reset;
- можно добавить подтверждение email.

В текущей версии проекта JWT/API-аутентификация в `main` не обнаружена. Она реализовывалась отдельно в ветке `feature/rest-api`, но не является частью текущей ветки `main`.

## 8. Валидация данных

В зоне пользователя валидируются:

- `username` в `CustomUserCreationForm.clean_username()` — минимум 5 символов;
- `email` в `CustomUserCreationForm.clean_email()` — обязательное поле;
- `password1`/`password2` — стандартной `UserCreationForm` и `AUTH_PASSWORD_VALIDATORS`;
- загружаемый `avatar` — стандартной логикой `ImageField`/Pillow при обработке файла.

Валидация важна, потому что пользовательская запись становится владельцем данных привычек. Неполные или слабые данные ухудшают безопасность и качество приложения.

## 9. Логирование

Logger создаётся в:

- `users/views.py`: `logger = logging.getLogger(__name__)`;
- `users/signals.py`: `logger = logging.getLogger(__name__)`;
- `config/settings.py`: logger `users` подключён к handlers.

События:

- `INFO` — успешная регистрация пользователя;
- `INFO` — успешный вход пользователя;
- `WARNING` — неудачная регистрация;
- `WARNING` — неудачная попытка входа.

Логи пишутся:

- в консоль через `StreamHandler`;
- в `logs/app.log` через `RotatingFileHandler`;
- в `logs/daily.log` через `TimedRotatingFileHandler`.

На практике это помогает понять, кто зарегистрировался, кто вошёл, почему пользователь не может войти и есть ли подозрительные попытки авторизации.

## 10. Тестирование

К зоне Dmitriy относятся тесты из `tests/test_users.py`.

Покрытые сценарии:

- успешная регистрация;
- ошибка регистрации при коротком username и пустом email;
- успешный login;
- logout и очистка session;
- доступность страницы смены пароля для авторизованного пользователя.

Fixtures используются из `tests/conftest.py`:

- `user`;
- `another_user`;
- `authenticated_client`;
- `TEST_PASSWORD`.

Запуск:

```bash
python -m pytest tests/test_users.py
```

В текущем окружении системная команда `python` отсутствует, поэтому фактически использовалась команда:

```bash
.venv/bin/python -m pytest tests/test_users.py
```

Через Docker:

```bash
docker compose exec web pytest tests/test_users.py
```

## 11. Покрытие тестами

Точный процент покрытия в текущем окружении не измерен, потому что:

- `python -m pytest --cov=. --cov-report=term-missing` не выполнился: системная команда `python` отсутствует;
- `.venv/bin/python -m pytest --cov=. --cov-report=term-missing` не выполнился: `pytest-cov` не установлен;
- `.venv/bin/python -m coverage run -m pytest` не выполнился: пакет `coverage` не установлен.

Фактический результат обычного тестового прогона:

```text
46 passed in 3.14s
```

Команда:

```bash
.venv/bin/python -m pytest
```

Как измерить покрытие после установки инструмента:

```bash
python -m pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

Для зоны Dmitriy лучше всего покрыты пользовательские сценарии регистрации, login/logout и password change. Хуже покрыты:

- `users/signals.py` как отдельные signal handlers;
- email password reset flow end-to-end;
- `users/admin.py`;
- отображение всех auth templates.

## 12. Docker / запуск / эксплуатация

Часть Dmitriy работает внутри Docker как обычный Django-код:

1. Контейнер `web` стартует Django через Gunicorn.
2. Settings читают `.env`.
3. `AUTH_USER_MODEL` подключает `users.CustomUser`.
4. Миграции создают таблицы пользователей и sessions.
5. Nginx проксирует HTTP-запросы к Django.
6. Auth templates рендерятся Django внутри контейнера.
7. Email backend берёт настройки из переменных окружения.

Для локального запуска без Docker:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Для Docker:

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Если используется файловый email backend, письма восстановления сохраняются в volume `sent_emails_data`, путь внутри контейнера `/app/sent_emails`.

## 13. Команды для проверки работы

Проверка проекта:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py runserver
```

Проверка auth/users:

```bash
python -m pytest tests/test_users.py
python -m pytest
```

Docker-команды:

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose logs -f web
docker compose down
```

Ручная проверка URL:

```text
/
/auth/register/
/auth/login/
/auth/logout/
/auth/password_change/
/auth/password_reset/
```

## 14. Возможные проблемы и способы решения

### Пользователь не может зарегистрироваться

Проверить:

- username должен быть минимум 5 символов;
- email обязателен;
- пароли должны совпадать;
- пароль должен проходить `AUTH_PASSWORD_VALIDATORS`;
- если загружается avatar, должен быть установлен Pillow.

### Пользователь не может войти

Проверить:

- пользователь существует;
- пароль верный;
- `is_active=True`;
- cookies включены в браузере;
- логи `users` и `django` в `logs/app.log`.

### После входа неправильный redirect

Проверить:

```python
LOGIN_REDIRECT_URL = "habit_list"
```

И наличие маршрута `habit_list` в `habits/urls.py`.

### Не отправляется письмо восстановления пароля

Для локального file backend проверить директорию `sent_emails/`. Для SMTP проверить `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

### Ошибка `no such table: users_customuser`

Не применены миграции:

```bash
python manage.py migrate
```

### Docker container не стартует

Проверить:

```bash
docker compose logs -f web
docker compose logs -f nginx
```

Частые причины: некорректный `.env`, неправильный `DJANGO_ALLOWED_HOSTS`, ошибка миграций.

## 15. Что можно улучшить

- Добавить полноценную страницу профиля пользователя.
- Добавить подтверждение email после регистрации.
- Добавить rate limiting для login/password reset.
- Добавить двухфакторную авторизацию.
- Добавить DRF REST API и Swagger в основную ветку после review ветки `feature/rest-api`.
- Добавить CI/CD с запуском `pytest`, `manage.py check`, `makemigrations --check`.
- Расширить тесты password reset flow.
- Добавить email notifications о привычках.
- Улучшить production deploy: HTTPS, secure cookies, PostgreSQL.

## 16. Итоговый вклад участника

Dmitriy Prihodin реализовал базовый каркас Django-проекта и пользовательский слой: главную страницу, кастомную модель `CustomUser`, регистрацию, стандартную авторизацию Django, auth templates, email backend и логирование auth-событий. Его вклад создал основу, на которой работают привычки, аналитика, права доступа и пользовательские сценарии всего Habit Tracker.
