# Продуктовый помощник Foodgram

## Описание
Данный проект представляет собой веб-сайт, на котором пользователи могут регистрироваться, публиковать свои рецепты, давая им описание, навешивая определенные теги, также могут добавлять рецепты других пользователей в избранное, подписываться на других пользователей и создавать свой список покупок, который потом можно скачать себе на устройство в виде pdf.

## Технологии
- Django Rest Framework, Django
- React
- PostgreSQL
- Nginx
- Docker
- Github actions

## Запуск проекта
1. Склонируйте репозиторий foodgram-project-react на свой компьютер.
```bash
git clone https://github.com/Mind-Insight/foodgram-project-react.git
```
2. Создайте виртуальное окружение проекта и активируйте его
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Установить зависимости из файла requirements.txt
```bash
pip install -r backend/requirements.txt
```
4. Создайте и заполните файл .env по примеру из .env.example
5. Запустите весь оркестр
```bash
sudo docker compose up
```
6. Скопируйте все необходимые фикстуры
```bash
docker compose cp ./backend/data/. backend:/app/foodgram/fixtures/
```
7. Примените миграции в контейнере и скопируйте статику
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
8. Подгрузите все данные из фикстур
```bash
docker compose exec backend python manage.py loaddata /app/foodgram/fixtures/ingredients.json
docker compose exec backend python manage.py loaddata /app/foodgram/fixtures/tags.json
```

сайт находится на https://foodgrammm.servebeer.com/