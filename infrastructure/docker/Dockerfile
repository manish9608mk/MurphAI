# MurphAI Backend + ML Docker Image

FROM python:3.12-slim

# Prevent Python from creating .pyc files
# and make logs appear immediately in Docker.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Application working directory
WORKDIR /app


# Install Python dependencies
COPY requirements.txt .

# Install Python dependencies without generating bytecode.
RUN pip install --no-cache-dir --no-compile --upgrade pip \
    && pip install --no-cache-dir --no-compile -r requirements.txt


# Copy application source
COPY backend ./backend
COPY ml ./ml
COPY alembic ./alembic
COPY alembic.ini .
COPY pytest.ini .


# Create directories required by the application.
RUN mkdir -p /app/ml/models \
    /app/ml/data \
    /app/mlruns


# Create a non-root user for running MurphAI.
RUN useradd --create-home --shell /bin/bash murphai


# Give the MurphAI user ownership of the application directory.
RUN chown -R murphai:murphai /app


# Run the application as the non-root MurphAI user.
USER murphai


# Expose FastAPI port
EXPOSE 8000


# Check whether the MurphAI API is responding.
# Docker marks the container unhealthy if this check fails.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=5)"


# Start MurphAI API
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]