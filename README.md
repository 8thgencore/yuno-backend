
## Setup database with initial data
This creates sample users on database.

*Using docker compose command*
```
docker compose -f docker-compose.yml exec web python app/initial_data.py
```

## Run Alembic migrations (Only if you change the DB model)

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web alembic revision --autogenerate
docker compose -f docker-compose.yml exec web alembic upgrade head
```
