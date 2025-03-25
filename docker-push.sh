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

# Log in to Docker Hub (will prompt for password)
echo "Logging in to Docker Hub..."
docker login --username $DOCKER_USERNAME

# Set up Docker Buildx for multi-platform builds
echo "Setting up Docker Buildx for multi-platform builds..."
docker buildx rm mybuilder 2>/dev/null || true
docker buildx create --name mybuilder --bootstrap --use

# Build multi-platform Docker image
echo "Building multi-platform Docker image..."
docker buildx build --platform linux/amd64 \
  --tag $DOCKER_USERNAME/$REPO_NAME:$VERSION \
  --tag $DOCKER_USERNAME/$REPO_NAME:latest \
  --push .

echo "Successfully pushed $DOCKER_USERNAME/$REPO_NAME:$VERSION to Docker Hub!"
echo "View your image at: https://hub.docker.com/r/$DOCKER_USERNAME/$REPO_NAME" 