# Yuno API

## Install

### Production

1. Copy file **.env.prod.example** to **.env.prod** and fill in 

2. *Using docker compose command*
```sh
docker compose -f docker-compose.prod.yml up -d --build 
```

### Development

1. Copy file **.env.example** to **.env** and fill in 

2. *Using docker compose command*
```sh
docker compose up -d --build
```

## Setup database with initial data

This creates sample users on database.

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web python -m app.initial_data
```

## Run Alembic migrations (Only if you change the DB model)

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web alembic revision --autogenerate
docker compose -f docker-compose.yml exec web alembic upgrade head
```
