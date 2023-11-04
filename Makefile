MANAGE = python manage.py
ccc:
	ls
run:
	$(MANAGE) runserver

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

worker:
	celery -A MyFruitShop worker -Q trading_queue,celery -l  info --concurrency=1
beat:
	celery -A MyFruitShop beat

dumpdata:
	$(MANAGE) dumpdata  -e contenttypes -e auth.Permission > db.json


startapp:
	$(MANAGE) migrate --no-input
	$(MANAGE) loaddata db.json
	$(MANAGE) collectstatic --no-input
	gunicorn MyFruitShop.wsgi:application --bind 0.0.0.0:8000

poetry-to-txt:
	poetry export --without-hashes --format=requirements.txt > requirements.txt


docker-build:
	sudo docker-compose -f docker-compose.yml build

docker-up:
	sudo docker-compose -f docker-compose.yml up

down:
	sudo docker compose down -v
prune:
	sudo docker  system prune -a


