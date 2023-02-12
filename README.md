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

You can connect to the Database using pgAdmin4 and use the credentials from .env file. Database port on local machine has been configured to **5454** on docker-compose-dev.yml file

(Optional) If you prefer you can run pgAdmin4 on a docker container using the following commands, they should executed on different terminals:

*Starts pgadmin*
```sh
# docker volume create pgadmin_data && \
docker compose -f pgadmin.yml up -d --force-recreate
```

*Load server configuration (It is required just the first time)*
```sh
docker exec -it pgadmin python /pgadmin4/setup.py --load-servers servers.json
```

This starts pgamin in [http://localhost:15432](http://localhost:15432).



## Run Alembic migrations (Only if you change the DB model)

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web alembic revision --autogenerate
docker compose -f docker-compose.yml exec web alembic upgrade head
```
