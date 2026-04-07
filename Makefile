.PHONY: up down restart logs clean network

# -------- CONFIG --------
APP = web
MANAGE = python manage.py
DC = docker compose exec $(APP)
NETWORK=research_registry_net

network:
	@docker network inspect $(NETWORK) >/dev/null 2>&1 || docker network create $(NETWORK)

up: network
	./start.sh

down:
	docker compose down -v
	docker network rm $(NETWORK) || true

clean:
	docker compose down -v --remove-orphans
	docker system prune -f

test:
	docker compose exec web coverage erase
	docker compose exec web coverage run manage.py test
	docker compose exec web coverage xml -o /app/coverage.xml
	docker compose exec web coverage html -d /app/htmlcov

lint:
	$(DC) ruff check .
	
lint-deep:
	$(DC) pylint applications accounts core studies participants

format:
	$(DC) ruff format .

# -------- UTIL --------
logs:
	docker compose logs -f