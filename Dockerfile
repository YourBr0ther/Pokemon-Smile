# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY tests/requirements-test.txt ./tests/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r tests/requirements-test.txt

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' appuser

COPY . .

# Install the package in development mode
RUN pip install -e .

USER appuser

EXPOSE 5001

# Use gunicorn for production with the correct module path
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app.app:app"]
