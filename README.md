# Всем привет ![](https://github.com/blackcater/blackcater/raw/main/images/Hi.gif) это Дипломная работа praktikum_new_diplom от [Яндекс Практикум](https://practicum.yandex.ru/)
<!---Результат тестирования-->
![example workflow](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)

***

[![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=anuraghazra&layout=compact)](https://github.com/anuraghazra/github-readme-stats)

## О проекте
«Фудграм» — это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также  доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

![](https://pictures.s3.yandex.net/resources/S16_01_1692340098.png)

## Структура проекта
Проект реализован по методологии REST API.

* **Бэкэнд**: Django + gunicorn
* **Фронтэнд**: React
* **База данных**: PosgreSQL
* **Статика**: nginх

## Настройка переменных окружения


## Развертывание
Проект собран в docker образы и загружен в [dockerhub](https://hub.docker.com/)

Для развертвания используйте foodgram  docker-compose.production.yml
```yaml


```
Запустите docker compose -f docker-compose.yml up -d



Установка проекта
Приложение запускается при помощи платформы Docker. Скачайте файл 'docker-compose.production.yml' из репозитория 'github.com/plotnik-pr/foodgram-project-react' и добавьте на ваш сервер в любую пустую папку. Перед запуском добавьте необходимые переменные окружения в файл '.env' в папке с проектом:

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY = 'SECRET_KEY'
DEBUG = 'True'
ALLOWED_HOSTS = 'HOST'
Для запуска проекта выполните команду

sudo docker compose -f docker-compose.production.yml up --build
Доступные эндпоинты
Ваш IP - главная страница проекта
Ваш IP/admin/ - страница администратора(суперпользователя) Вместо Ваш_IP может быть использован домен.