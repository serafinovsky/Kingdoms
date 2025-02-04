FROM python:3.13.2-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_ROOT='/opt/projects/app' \ 
    HOME="/home/appuser"

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install poetry==2.1.1

RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -u ${USER_ID} -g appuser -m -s /bin/bash appuser && \
    mkdir -p ${APP_ROOT} && chown -R appuser:appuser ${APP_ROOT}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

ENV POETRY_HOME="$HOME/.poetry" \
    POETRY_VIRTUALENVS_PATH="$HOME/.virtualenvs" \
    POETRY_CACHE_DIR="$HOME/.cache/pypoetry" 

ENV PATH="$POETRY_HOME/bin:$HOME/.venv/bin:$PATH"

USER appuser
WORKDIR ${HOME}
COPY --chown=appuser:appuser pyproject.toml poetry.lock ${HOME}
RUN poetry install -v --no-root && mkdir -p media
WORKDIR ${APP_ROOT}