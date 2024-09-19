# -----------------------------------------------------------------------------
# Base stage
# -----------------------------------------------------------------------------
# pull official base image
FROM python:3.11-slim-buster AS base

# install system dependencies
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends curl git build-essential netcat gcc postgresql \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

# Install poetry using the official script
ENV POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 -

# -----------------------------------------------------------------------------
# Install stage
# -----------------------------------------------------------------------------
FROM base AS install

# set working directory
WORKDIR /usr/src

# allow controlling the poetry installation of dependencies via external args
ARG INSTALL_ARGS="--no-root"
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
COPY pyproject.toml poetry.lock ./

# install without virtualenv, since we are inside a container
RUN poetry config virtualenvs.create false \
  && poetry install $INSTALL_ARGS

# cleanup
RUN curl -sSL https://install.python-poetry.org | python3 - --uninstall \
  && apt-get purge -y curl git build-essential gcc \
  && apt-get clean -y \
  && rm -rf /root/.cache /var/apt/lists/* /var/cache/apt/*

# -----------------------------------------------------------------------------
# App-image stage
# -----------------------------------------------------------------------------
FROM install AS app-image

# set working directory
WORKDIR /usr/src

# run fastapi project
COPY ./deploy/local/start /start
RUN sed -i 's/\r$//g' /start \
  && chmod +x /start

# run celery worker
COPY ./deploy/local/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker \
  && chmod +x /start-celeryworker

# run flower
COPY ./deploy/local/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower \
  && chmod +x /start-flower

# add app
COPY . .

# chmod entrypoint.sh
RUN chmod +x /usr/src/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]
