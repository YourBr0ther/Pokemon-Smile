#!/bin/bash
# Simple helper script for Docker Compose operations on Mac/Linux

# Function to check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Docker is installed
if ! command_exists docker; then
  echo "Error: Docker is not installed or not in your PATH"
  echo "Please install Docker first: https://docs.docker.com/get-docker/"
  exit 1
fi

# Check Docker service
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker service is not running"
  echo "On Mac: Start the Docker Desktop application"
  echo "On Linux: Run 'sudo service docker start'"
  exit 1
fi

# Execute commands based on argument
case "$1" in
  start)
    echo "Starting Pokemon Smile in detached mode..."
    docker compose up -d
    echo "Services started! Access the app at http://localhost:5000"
    ;;
  stop)
    echo "Stopping all services..."
    docker compose down
    ;;
  logs)
    echo "Showing logs (Ctrl+C to exit)..."
    docker compose logs -f
    ;;
  build)
    echo "Rebuilding containers..."
    docker compose build --no-cache
    docker compose up -d
    ;;
  clean)
    echo "Stopping services and removing volumes..."
    docker compose down -v
    ;;
  restart)
    echo "Restarting all services..."
    docker compose restart
    ;;
  *)
    echo "Pokemon Smile Docker Helper"
    echo "Usage: $0 {start|stop|logs|build|clean|restart}"
    exit 1
    ;;
esac

exit 0 