#!/bin/bash
# Script to build and publish the Pokemon Smile Docker image to Docker Hub

# Replace with your Docker Hub username
DOCKER_USERNAME="yourbr0ther"
REPO_NAME="pokemon-smile"
VERSION="1.0.0"

# Function to check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Docker is installed and running
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

# Check if Docker Buildx is available
if ! docker buildx version >/dev/null 2>&1; then
  echo "Setting up Docker Buildx..."
  docker buildx create --name multiplatform --use
fi

# Build multi-platform Docker image
echo "Building multi-platform Docker image..."
docker buildx build --platform linux/amd64,linux/arm64 \
  --tag $DOCKER_USERNAME/$REPO_NAME:$VERSION \
  --tag $DOCKER_USERNAME/$REPO_NAME:latest \
  --push .

# Log in to Docker Hub (will prompt for password)
echo "Logging in to Docker Hub..."
docker login --username $DOCKER_USERNAME

echo "Successfully pushed $DOCKER_USERNAME/$REPO_NAME:$VERSION to Docker Hub!"
echo "View your image at: https://hub.docker.com/r/$DOCKER_USERNAME/$REPO_NAME" 