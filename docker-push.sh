#!/bin/bash
# Script to build and publish the Pokemon Smile Docker image to Docker Hub

# Replace with your Docker Hub username
DOCKER_USERNAME="yourusername"
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

# Build the Docker image
echo "Building Docker image..."
docker build -t $DOCKER_USERNAME/$REPO_NAME:$VERSION .
docker tag $DOCKER_USERNAME/$REPO_NAME:$VERSION $DOCKER_USERNAME/$REPO_NAME:latest

# Log in to Docker Hub (will prompt for password)
echo "Logging in to Docker Hub..."
docker login --username $DOCKER_USERNAME

# Push the images to Docker Hub
echo "Pushing images to Docker Hub..."
docker push $DOCKER_USERNAME/$REPO_NAME:$VERSION
docker push $DOCKER_USERNAME/$REPO_NAME:latest

echo "Successfully pushed $DOCKER_USERNAME/$REPO_NAME:$VERSION to Docker Hub!"
echo "View your image at: https://hub.docker.com/r/$DOCKER_USERNAME/$REPO_NAME" 