# Yuno API

## Install

### Production

1. Copy file **.env.prod.example** to **.env** and fill in 

*Using docker compose command*
```sh
docker compose -f docker-compose.prod.yml up -d --build 
```

*Using Makefile command*
```sh
make run-prod-build
```

### Development

1. Copy file **.env.example** to **.env** and fill in 
  
*Using docker compose command*
```sh
docker compose up -d --build
```

*Using Makefile command*
```sh
make run-dev-build
```

## Setup database with initial data

This creates sample users on database.

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web python -m app.initial_data
```

*Using Makefile command*
```sh
make init-db
```

You can connect to the Database using pgAdmin4 and use the credentials from .env file. Database port on local machine has been configured to **5454** on docker-compose-dev.yml file

(Optional) If you prefer you can run pgAdmin4 on a docker container using the following commands, they should executed on different terminals:

*Starts pgadmin*
```sh
make pgadmin-run
```

*Load server configuration (It is required just the first time)*
```sh
make pgadmin-load-server
```

*Remove pgadmin volume*
```sh
make pgadmin-clean
```



This starts pgamin in [http://localhost:15432](http://localhost:15432).



## Run Alembic migrations (Only if you change the DB model)

*Using docker compose command*
```sh
docker compose -f docker-compose.yml exec web alembic revision --autogenerate
docker compose -f docker-compose.yml exec web alembic upgrade head
```

*Using Makefile command*
```sh
make add-dev-migration
```
