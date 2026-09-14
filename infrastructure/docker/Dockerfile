# MurphAI Backend + ML Docker Image

FROM python:3.12-slim


# Python runtime configuration

# Prevent Python from creating .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python logs appear immediately in Docker.
ENV PYTHONUNBUFFERED=1


# Application working directory

WORKDIR /app


# Install Python dependencies

COPY requirements.txt .

RUN pip install --no-cache-dir --no-compile --upgrade pip \
    && pip install --no-cache-dir --no-compile -r requirements.txt


# Create the MurphAI application user

# The application should not run as root inside the container.
RUN useradd \
    --create-home \
    --shell /bin/bash \
    murphai


# Copy application source

COPY backend ./backend
COPY ml ./ml
COPY alembic ./alembic
COPY alembic.ini .
COPY pytest.ini .


# Create application storage directories

# These directories are used by MLflow for its SQLite
# tracking database and model artifacts.
#
# They must exist before Docker mounts the named volumes
# so the mounted volumes inherit the correct ownership.
RUN mkdir -p \
    /app/.mlflow \
    /app/mlruns \
    /app/ml/models \
    /app/ml/data


# Give the application user ownership of the entire
# application directory and its writable storage paths.
RUN chown -R \
    murphai:murphai \
    /app


# Run MurphAI as a non-root user

USER murphai


# Expose FastAPI port

EXPOSE 8000


# Container healthcheck

# The API is considered healthy only when its readiness
# endpoint confirms that the application can access its
# required runtime dependencies.
HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=5)"


# Start MurphAI API

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
