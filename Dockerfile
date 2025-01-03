FROM python:3.12.3-slim
LABEL maintainer="94nj111@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POETRY_VIRTUALENVS_CREATE=false

RUN mkdir -p /files/media

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN chown -R appuser /files/media
RUN chmod -R 755 /files/media

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry install --no-dev --no-interaction --no-ansi

USER appuser

COPY . .

EXPOSE 8000
