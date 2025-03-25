# PowerShell script for Docker Compose operations on Windows

param (
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("start", "stop", "logs", "build", "clean", "restart")]
    [string]$Command
)

switch ($Command) {
    "start" {
        Write-Host "Starting Pokemon Smile in detached mode..."
        docker compose up -d
        Write-Host "Services started! Access the app at http://localhost:5000"
    }
    "stop" {
        Write-Host "Stopping all services..."
        docker compose down
    }
    "logs" {
        Write-Host "Showing logs (Ctrl+C to exit)..."
        docker compose logs -f
    }
    "build" {
        Write-Host "Rebuilding containers..."
        docker compose build --no-cache
        docker compose up -d
    }
    "clean" {
        Write-Host "Stopping services and removing volumes..."
        docker compose down -v
    }
    "restart" {
        Write-Host "Restarting all services..."
        docker compose restart
    }
    default {
        Write-Host "Pokemon Smile Docker Helper"
        Write-Host "Usage: .\docker-start.ps1 {start|stop|logs|build|clean|restart}"
        exit 1
    }
} 