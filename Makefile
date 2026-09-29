.PHONY: up down logs migrate psql lint fmt

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	docker compose run --rm api alembic upgrade head

psql:
	docker compose exec db psql -U crop -d crop_fields

lint:
	ruff check . && ruff format --check .

fmt:
	ruff check --fix . && ruff format .
