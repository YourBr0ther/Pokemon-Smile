# PowerShell script to build and publish the Pokemon Smile Docker image to Docker Hub

# Replace with your Docker Hub username
$DOCKER_USERNAME = "yourbr0ther"
$REPO_NAME = "pokemon-smile"
$VERSION = "1.0.0"

# Build the Docker image
Write-Host "Building Docker image..."
docker build -t "$DOCKER_USERNAME/$REPO_NAME:$VERSION" .
docker tag "$DOCKER_USERNAME/$REPO_NAME:$VERSION" "$DOCKER_USERNAME/$REPO_NAME:latest"

# Log in to Docker Hub (will prompt for password)
Write-Host "Logging in to Docker Hub..."
docker login --username $DOCKER_USERNAME

# Push the images to Docker Hub
Write-Host "Pushing images to Docker Hub..."
docker push "$DOCKER_USERNAME/$REPO_NAME:$VERSION"
docker push "$DOCKER_USERNAME/$REPO_NAME:latest"

Write-Host "Successfully pushed $DOCKER_USERNAME/$REPO_NAME:$VERSION to Docker Hub!"
Write-Host "View your image at: https://hub.docker.com/r/$DOCKER_USERNAME/$REPO_NAME" 