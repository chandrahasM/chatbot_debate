.PHONY: all install test run down clean

# Default target - shows all available commands
all:
	@echo "Available commands:"
	@echo "  make install - Install all requirements to run the service"
	@echo "  make test    - Run tests"
	@echo "  make run     - Run the service and all related services in Docker"
	@echo "  make down    - Teardown of all running services"
	@echo "  make clean   - Teardown and removal of all containers"

install:
	@echo "Installing requirements..."
	@command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || { echo "Python3 is required. Install it from https://www.python.org/downloads/"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required. Install it from https://docs.docker.com/get-docker/"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || { echo "Docker Compose is required. Install it from https://docs.docker.com/compose/install/"; exit 1; }
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installation complete!"

test:
	@echo "Running tests..."
	pytest tests/ -v
	@echo "Tests completed!"

run:
	@echo "Starting the debate chatbot service..."
	docker-compose up --build

down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "Services stopped."

clean:
	@echo "Cleaning up containers and images..."
	docker-compose down -v --rmi all
	@if [ -f chat.db ]; then rm -f chat.db; echo "Removed chat.db"; fi
	@echo "Cleanup complete!"
