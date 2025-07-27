#!/usr/bin/env pwsh
# PowerShell script equivalent to Makefile for Windows users

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:"
    Write-Host "  .\run.ps1 install - Install all requirements to run the service"
    Write-Host "  .\run.ps1 test    - Run tests"
    Write-Host "  .\run.ps1 run     - Run the service and all related services in Docker"
    Write-Host "  .\run.ps1 down    - Teardown of all running services"
    Write-Host "  .\run.ps1 clean   - Teardown and removal of all containers"
}

function Install-Requirements {
    Write-Host "Installing requirements..."
    
    # Check for Python
    try {
        $null = Get-Command python -ErrorAction Stop
        Write-Host "✓ Python found"
    } catch {
        try {
            $null = Get-Command python3 -ErrorAction Stop
            Write-Host "✓ Python3 found"
        } catch {
            Write-Error "Python3 is required. Install it from https://www.python.org/downloads/"
            exit 1
        }
    }
    
    # Check for Docker
    try {
        $null = Get-Command docker -ErrorAction Stop
        Write-Host "✓ Docker found"
    } catch {
        Write-Error "Docker is required. Install it from https://docs.docker.com/get-docker/"
        exit 1
    }
    
    # Check for Docker Compose
    try {
        $null = docker compose version
        Write-Host "✓ Docker Compose found"
    } catch {
        try {
            $null = Get-Command docker-compose -ErrorAction Stop
            Write-Host "✓ Docker Compose found"
        } catch {
            Write-Error "Docker Compose is required. Install it from https://docs.docker.com/compose/install/"
            exit 1
        }
    }
    
    Write-Host "Installing Python dependencies..."
    pip install -r requirements.txt
    Write-Host "Installation complete!"
}

function Run-Tests {
    Write-Host "Running tests..."
    pytest tests/ -v
    Write-Host "Tests completed!"
}

function Start-Service {
    Write-Host "Starting the debate chatbot service..."
    docker compose up --build
}

function Stop-Service {
    Write-Host "Stopping all services..."
    docker compose down
    Write-Host "Services stopped."
}

function Clean-All {
    Write-Host "Cleaning up containers and images..."
    docker compose down -v --rmi all
    if (Test-Path "chat.db") {
        Remove-Item "chat.db"
        Write-Host "Removed chat.db"
    }
    Write-Host "Cleanup complete!"
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Requirements }
    "test" { Run-Tests }
    "run" { Start-Service }
    "down" { Stop-Service }
    "clean" { Clean-All }
    default { 
        Write-Host "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
