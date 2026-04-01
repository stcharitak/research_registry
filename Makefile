# -------- CONFIG --------
APP = web
MANAGE = python manage.py
DC = docker compose exec $(APP)

run:
	./start.sh

down:
	docker compose down -v

test:
	docker compose exec web coverage erase
	docker compose exec web coverage run manage.py test
	docker compose exec web coverage xml -o /app/coverage.xml
	docker compose exec web coverage html -d /app/htmlcov

lint:
	$(DC) ruff check .

format:
	$(DC) ruff format .

# -------- UTIL --------
logs:
	docker compose logs -f