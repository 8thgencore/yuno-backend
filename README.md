# Yuno API

## Install

### Production

1. Copy file **.env.prod.example** to **.env** and fill in

Create network

```sh
docker network create external_network
```

_Using docker compose command_

```sh
docker compose -f docker-compose.prod.yml up -d --build
```

_Using Makefile command_

```sh
make run-prod-build
```

### Development

1. Copy file **.env.example** to **.env** and fill in

_Using docker compose command_

```sh
docker compose up -d --build
```

_Using Makefile command_

```sh
make run-dev-build
```

## Setup database with initial data

This creates sample users on database.

_Using docker compose command_

```sh
docker compose -f docker-compose.yml exec web python -m app.initial_data
```

_Using Makefile command_

```sh
make init-db
```

You can connect to the Database using pgAdmin4 and use the credentials from .env file. Database port on local machine has been configured to **5454** on docker-compose-dev.yml file

(Optional) If you prefer you can run pgAdmin4 on a docker container using the following commands, they should executed on different terminals:

_Starts pgadmin_

```sh
make pgadmin-run
```

_Load server configuration (It is required just the first time)_

```sh
make pgadmin-load-server
```

_Remove pgadmin volume_

```sh
make pgadmin-clean
```

This starts pgamin in [http://localhost:15432](http://localhost:15432).

## Run Alembic migrations (Only if you change the DB model)

_Using docker compose command_

```sh
docker compose -f docker-compose.yml exec web alembic revision --autogenerate
docker compose -f docker-compose.yml exec web alembic upgrade head
```

_Using Makefile command_

```sh
make add-dev-migration
```

## Mail Client for send otp code

[Link to the microservice **Mailfort** ](https://github.com/8thgencore/mailfort)

### Generating files from .proto for mail:
Execute the following command in the `src` directory of your project:

```bash
python -m grpc_tools.protoc -I=./proto --python_out=./app/generated/ --grpc_python_out=./app/generated/ ./proto/mail/mail.proto
```

This command will generate Python files for protobuf and gRPC in the `./src/proto/generated/` directory.
