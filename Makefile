# AI Media Analysis System - Makefile
# Vereinfacht Test-Ausführung und Entwicklungsaufgaben

.PHONY: help install test test-unit test-integration test-e2e test-performance
.PHONY: test-coverage test-lint test-security test-docker test-all 
.PHONY: format lint clean setup dev-setup ci-setup
.PHONY: run-services stop-services restart-services health-check

# Default target
help: ## Zeigt diese Hilfe an
	@echo "AI Media Analysis System - Entwicklungskommandos"
	@echo ""
	@echo "Verfügbare Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation und Setup
install: ## Installiert alle Abhängigkeiten
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev-setup: install ## Setup für Entwicklungsumgebung
	@echo "🛠️  Setting up development environment..."
	python run_tests.py --check-env
	pre-commit install || echo "pre-commit not available"

ci-setup: install ## Setup für CI/CD-Umgebung
	@echo "🔧 Setting up CI environment..."
	python run_tests.py --check-env

# Test-Ausführung
test: ## Führt alle Tests aus (ohne E2E und Performance)
	@echo "🧪 Running all tests..."
	python run_tests.py -v

test-unit: ## Führt nur Unit Tests aus
	@echo "🔬 Running unit tests..."
	python run_tests.py --unit -v

test-integration: ## Führt nur Integration Tests aus
	@echo "🔗 Running integration tests..."
	python run_tests.py --integration -v

test-e2e: ## Führt nur End-to-End Tests aus
	@echo "🎯 Running end-to-end tests..."
	python run_tests.py --e2e -v

test-performance: ## Führt nur Performance Tests aus
	@echo "⚡ Running performance tests..."
	python run_tests.py --performance -v

test-docker: ## Führt Docker-basierte Tests aus
	@echo "🐳 Running Docker tests..."
	python run_tests.py --docker -v

test-coverage: ## Führt Tests mit Coverage-Analyse aus
	@echo "📊 Running tests with coverage..."
	python run_tests.py --coverage -v
	@echo "📈 Coverage report: htmlcov/index.html"

test-all: ## Führt komplette Test-Suite aus
	@echo "🚀 Running comprehensive test suite..."
	python run_tests.py --all -v

# Code-Qualität
lint: ## Führt Code-Linting aus
	@echo "🧹 Running code linting..."
	python run_tests.py --lint

format: ## Formatiert Code mit black und isort
	@echo "🎨 Formatting code..."
	python -m black services tests
	python -m isort services tests
	@echo "✅ Code formatting completed"

test-security: ## Führt Security-Scan aus
	@echo "🔒 Running security scan..."
	python run_tests.py --security

# Service-Management (Docker)
run-services: ## Startet alle Services mit Docker Compose
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 30
	@make health-check

stop-services: ## Stoppt alle Services
	@echo "🛑 Stopping all services..."
	docker-compose down

restart-services: stop-services run-services ## Startet alle Services neu

health-check: ## Überprüft Service-Health
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Main API not healthy"
	@curl -f http://localhost:8001/health || echo "❌ LLM Service not healthy"
	@curl -f http://localhost:8002/health || echo "❌ Vector DB not healthy"
	@curl -f http://localhost:8003/health || echo "❌ Whisper Service not healthy"

# Service-spezifische Tests
test-llm-service: ## Testet nur LLM Service
	@echo "🤖 Testing LLM Service..."
	python -m pytest services/llm_service/tests/ -v

test-vision-service: ## Testet nur Vision Pipeline
	@echo "👁️  Testing Vision Pipeline..."
	python -m pytest services/vision_pipeline/tests/ -v

test-vector-db: ## Testet nur Vector Database
	@echo "🗄️  Testing Vector Database..."
	python -m pytest services/vector_db/tests/ -v

test-whisper-service: ## Testet nur Whisper Service
	@echo "🎤 Testing Whisper Service..."
	python -m pytest services/whisper_service/tests/ -v

# Entwicklungstools
clean: ## Bereinigt temporäre Dateien
	@echo "🧽 Cleaning up..."
	python run_tests.py --cleanup
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
	@echo "✅ Cleanup completed"

setup: dev-setup ## Alias für dev-setup

# Quick-Commands für CI/CD
ci-test: test-lint test-unit test-integration ## CI-Pipeline Tests

pre-commit: format lint test-unit ## Pre-commit Hook

# Dokumentation
docs: ## Generiert Dokumentation
	@echo "📚 Generating documentation..."
	@echo "TODO: Add documentation generation"

# Utility-Targets
check-deps: ## Überprüft Abhängigkeiten auf Updates
	@echo "🔍 Checking for dependency updates..."
	pip list --outdated

install-dev-tools: ## Installiert zusätzliche Entwicklungstools
	@echo "🛠️  Installing development tools..."
	pip install bandit safety pre-commit

update-deps: ## Aktualisiert Abhängigkeiten
	@echo "⬆️  Updating dependencies..."
	pip install --upgrade -r requirements.txt

# Spezielle Test-Modi
test-fast: test-unit ## Schnelle Tests (nur Unit Tests)

test-slow: test-integration test-e2e test-performance ## Langsame Tests

test-ci: ci-test test-coverage ## Vollständige CI-Tests

# Service-Logs
logs: ## Zeigt Docker Service Logs
	docker-compose logs -f

logs-llm: ## Zeigt LLM Service Logs
	docker-compose logs -f llm-service

logs-vision: ## Zeigt Vision Pipeline Logs
	docker-compose logs -f vision-pipeline

logs-vector: ## Zeigt Vector DB Logs
	docker-compose logs -f vector-db

logs-whisper: ## Zeigt Whisper Service Logs
	docker-compose logs -f whisper-service

# Monitoring
monitor: ## Zeigt Service-Status
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "💾 Disk Usage:"
	@df -h | head -n 2
	@echo ""
	@echo "🧠 Memory Usage:"
	@free -h
	@echo ""
	@echo "⚙️  CPU Usage:"
	@top -bn1 | grep "Cpu(s)" | head -n 1

# Default Python und Test-Runner
PYTHON := python3
TEST_RUNNER := $(PYTHON) run_tests.py

# Override für verschiedene Python-Versionen
test-python39:
	@echo "🐍 Testing with Python 3.9..."
	python3.9 run_tests.py --unit -v

test-python310:
	@echo "🐍 Testing with Python 3.10..."
	python3.10 run_tests.py --unit -v

test-python311:
	@echo "🐍 Testing with Python 3.11..."
	python3.11 run_tests.py --unit -v 