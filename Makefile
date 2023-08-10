#!/usr/bin/make

include .env

define SERVERS_JSON
{
	"Servers": {
		"1": {
			"Name": "yuno-database",
			"Group": "Servers",
			"Host": "$(DB_HOST)",
			"Port": $(DB_PORT),
			"MaintenanceDB": "postgres",
			"Username": "$(DB_USER)",
			"SSLMode": "prefer",
			"PassFile": "/tmp/pgpassfile"
		}
	}
}
endef
export SERVERS_JSON

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally."
	@echo "    run-dev-build"
	@echo "        Run development docker compose and force build containers."
	@echo "    run-dev"
	@echo "        Run development docker compose."
	@echo "    stop-dev"
	@echo "        Stop development docker compose."
	@echo "    run-prod-build"
	@echo "        Run production docker compose and force build containers."
	@echo "    run-prod"
	@echo "        Run production docker compose."
	@echo "    stop-prod"
	@echo "        Run production docker compose."
	@echo "    pytest"
	@echo "        Run pytest."	
	@echo "    init-db"
	@echo "        Init database with sample data."	
	@echo "    migrations"
	@echo "        Creates a new migration script autogenerate feature."
	@echo "    migrate"
	@echo "        Applies the migration to the database."
	@echo "    pgadmin-run"
	@echo "        Run pgadmin4."	
	@echo "    pgadmin-load-server"
	@echo "        Load server on pgadmin4."
	@echo "    pgadmin-clean"
	@echo "        Clean pgadmin4 data."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    mypy"
	@echo "        Static type checker."	
	@echo "    lint"
	@echo "        Lint code with ruff, and check if black formatter should be applied."
	@echo "    lint-watch"
	@echo "        Lint code with ruff in watch mode."
	@echo "    lint-fix"
	@echo "        Lint code with ruff and try to fix."	


install:
	cd src && \
	poetry shell && \
	poetry install

run-dev-build:
	docker compose up -d --build

run-dev:
	docker compose up -d

stop-dev:
	docker compose down

run-prod-build:
	docker compose -f docker-compose.prod.yml up -d --build

run-prod:
	docker compose -f docker-compose.prod.yml up -d

stop-prod:
	docker compose -f docker-compose.prod.yml down

pytest:
	docker compose -f docker-compose.yml exec web pytest

init-db:
	docker compose -f docker-compose.yml exec web python -m app.initial_data && \
	echo "Initial data created." 

formatter:
	cd src && \
	poetry run black app

mypy:
	cd src && \
	poetry run mypy --ignore-missing-imports app

lint:
	cd src && \
	poetry run ruff app && poetry run black --check app

lint-watch:
	cd src && \
	poetry run ruff app --watch

lint-fix:
	cd src && \
	poetry run ruff app --fix

migrations:
	docker compose -f docker-compose.yml exec web alembic revision --autogenerate

migrate:
	docker compose -f docker-compose.yml exec web alembic upgrade head 

pgadmin-run:
	echo "$$SERVERS_JSON" > ./pgadmin/servers.json && \
	docker volume create pgadmin_data && \
	docker compose -f pgadmin.yml up --force-recreate
	
pgadmin-load-server:
	docker exec -it pgadmin python /pgadmin4/setup.py --load-servers servers.json

pgadmin-clean:
	docker volume rm pgadmin_data
