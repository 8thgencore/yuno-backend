
## Setup database with initial data
This creates sample users on database.

*Using docker compose command*
```
docker compose -f docker-compose-dev.yml exec fastapi_server python app/initial_data.py
```

## Run Alembic migrations (Only if you change the DB model)

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec yuno-app-container alembic revision --autogenerate
docker compose -f docker-compose.yml exec yuno-app-container alembic upgrade head
```

