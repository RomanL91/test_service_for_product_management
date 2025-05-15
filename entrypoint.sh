#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

python -m celery -A core.celery worker -l info -c 2 -P eventlet &
python -m celery -A core beat -l info &
python -m celery -A core flower --port=8001 --basic_auth=admin:admin &

# запуск скрипта для потребление очереди, где хранится результат парсинга
# python manage.py consumer_spec --host=185.100.67.246 --queue=returned_spec &

# запуск потрибителя для готовых переводов
python manage.py start_consumer &

# python manage.py search_index --rebuild -f

# gunicorn --bind 0.0.0.0:8000 core.asgi -w 4 -k uvicorn.workers.UvicornWorker # с возможностью указания количества воркеров
uvicorn core.asgi:application --host 0.0.0.0 --port 8888