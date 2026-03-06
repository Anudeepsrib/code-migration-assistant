# Multi-stage Dockerfile for Code Migration Assistant

# 1. Base Image
FROM python:3.13-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# 2. Builder Stage
FROM python-base AS builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# We'll use standard requirements.txt for simplicity in this build context since pyproject.toml 
# is currently setup for standard pip build
WORKDIR $PYSETUP_PATH
COPY pyproject.toml .
COPY requirements.txt .

# Install dependencies into virtualenv
RUN python -m venv $VENV_PATH && \
    . $VENV_PATH/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 3. UI Builder Stage
FROM node:20-slim AS ui-builder

WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm ci

COPY ui/ ./
RUN npm run build

# 4. Final Production Stage
FROM python-base AS production
LABEL maintainer="Enterprise Modernization Team"

# Create unprivileged user
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder $VENV_PATH $VENV_PATH

# Copy built UI static files
COPY --from=ui-builder /app/ui/dist /app/ui/dist

# Set up application directory
WORKDIR /app
COPY src/ ./src/
COPY pyproject.toml ./
COPY config.defaults.yaml ./
COPY README.md ./

# Install the application package itself into the venv
RUN . $VENV_PATH/bin/activate && pip install -e .

# Create logs directory with correct permissions
RUN mkdir -p /app/.migration-logs && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Metadata
ENV MIGRATION_SERVER__HOST="0.0.0.0"
ENV MIGRATION_SERVER__PORT=8000
ENV MIGRATION_OBSERVABILITY__LOG_FORMAT="json"

CMD ["uvicorn", "code_migration.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
