# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' appuser
USER appuser

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
