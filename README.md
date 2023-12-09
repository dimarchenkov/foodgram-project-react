<!---Результат тестирования-->
![example workflow](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)

***
# Foodgram [Яндекс Практикум](https://practicum.yandex.ru/)

## Описание проекта
«Фудграм» — это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также  доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

![](https://pictures.s3.yandex.net/resources/S16_01_1692340098.png)

## Инструкция по развертыванию
Проект собран в docker образы и загружен в [dockerhub](https://hub.docker.com/)

### Локальный запуск проекта
Клонируейте репозиторий с проектом:
```
git clone https://github.com/dimarchenkov/foodgram-project-react.git && cd foodgram-project-react
Создайте виртуальное окружение
```
python -m venv .venv
```

Активируйте виртуальное окружение
```
source .venv/bin/activate
```

Установите библиотеки python
```
pip install --upgrade pip && pip install -r requirements.txt
```

Выполните миграцию базы данных
```
python3 python3 manage.py migrate
```

Создайте суперпользователя
```
python3 manage.py createsuperuser
```

Заполните базу данных
```
python3 manage.py load_tags
python3 manage.py load_ingredients
```
Запустите проект
```
python3 manage.py runserver 127.0.0.1:8000
```

### Запуск проекта в docker
Установите [docker](https://docs.docker.com/engine/install/)

Для развертвания на сервере используйте `docker-compose.production.yml`
```yaml
version: '3.3'
volumes:
  pg_data:
  static:
  media:
services:
  db:
    image: postgres
    restart: always
    env_file: .env.example
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}" ]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - pg_data:/var/lib/postgresql/data
  backend:
    image: dmitriy1223/foodgram_backend
    depends_on:
      - db
    env_file: .env.example
    volumes:
      - static:/static_backend
      - media:/media_files
  nginx:
    image: dmitriy1223/foodgram_gateway
    ports:
      - "9000:80"
    volumes:
      - media:/media_files
      - static:/static_backend
```

Создайте файл переменных `.env.example`
```bash
DJANGO_SECRET_KEY=Секретный_ключ
DJANGO_SERVER_TYPE=prod
DJANGO_ALLOWED_HOSTS=127.0.0.1,locahost
POSTGRES_USER=django_user
POSTGRES_PASSWORD=Пароль
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

Запустите проект:
```docker compose -f docker-compose.yml up -d```

Настройте проект:
```bash
sudo docker compose -f docker-compose.production.yml -p foodgram exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml -p foodgram exec backend python manage.py load_ingredients
sudo docker compose -f docker-compose.production.yml -p foodgram exec backend python manage.py load_tags
sudo docker compose -f docker-compose.production.yml -p foodgram exec backend python manage.py collectstatic
```

### Доступные эндпоинты
[IP адрес или домен] - главная страница проекта
[IP адрес или домен]/admin/ - страница администратора(суперпользователя)

## Стэк технологий
Проект реализован по методологии REST API.

* **Бэкэнд**: Django + gunicorn
* **Фронтэнд**: React
* **База данных**: PosgreSQL
* **Статика**: nginх

## Документация
Документация сделана с использованием Redoc на основе описания OpenAPI.

Доступна по ссылке `[site]/api/docs` после запуска проекта.

## Пример запросов и ответов
Пример запроса списка пользователей:
```
[GET] http://localhost/api/users/
```

Пример ответа:
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}

```
Запрос на лобавление рецепта в избранное:
```
[POST] http://localhost/api/recipes/{id}/favorite/
```

Ответ:
```json
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
"cooking_time": 1
}
```
## Автор
[Дмитрий М.](https://github.com/dimarchenkov/foodgram-project-react)
## Пример
Пример сайта доступен по адресу:
[https://foodgram-project.site](https://foodgram-project.site)