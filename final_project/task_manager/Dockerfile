# Multistage image, based on https://pythonspeed.com/articles/multi-stage-docker-python/
ARG CI_PUBLIC_REGISTRY=docker.io
FROM ${CI_PUBLIC_REGISTRY}/python:3.9 AS compile-image

ARG PYPI_USERNAME
ARG PYPI_PASSWORD


RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc git ssh

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DOCKER_CONTAINER=1 \
    PYPI_USERNAME=$PYPI_USERNAME \
    PYPI_PASSWORD=$PYPI_PASSWORD \
    POETRY_VERSION=1.1.8

WORKDIR /app/

COPY ./poetry.lock ./pyproject.toml /app/

RUN pip install poetry==$POETRY_VERSION
RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry config experimental.new-installer false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    rm -rf $POETRY_CACHE_DIR
#=====================================================
FROM compile-image as develop

RUN poetry install --no-interaction --no-ansi
COPY . /app

RUN chmod +x /app/docker/scripts/docker-entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["/app/docker/scripts/docker-entrypoint.sh"]

# ====================================================
FROM ${CI_PUBLIC_REGISTRY}/python:3.9-slim AS production

RUN adduser --uid 1000 --home /app --disabled-password --gecos "" popug && \
    chown -hR popug: /app

WORKDIR /app/

COPY --chown=popug:popug . /app/
COPY --from=compile-image /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x /app/docker/scripts/docker-entrypoint.sh

USER popug

ENTRYPOINT ["/app/docker/scripts/docker-entrypoint.sh"]
CMD ["help"]
