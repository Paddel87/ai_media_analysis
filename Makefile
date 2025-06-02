# AI Media Analysis System - VPS-Optimiertes Makefile
# Vereinfacht Test-Ausführung und VPS-Development-Aufgaben

.PHONY: help install test test-unit test-integration test-e2e test-performance
.PHONY: test-coverage test-lint test-security test-docker test-all
.PHONY: format lint clean setup dev-setup ci-setup
.PHONY: run-services stop-services restart-services health-check
.PHONY: vps-setup vps-deploy vps-test logs-all monitor
.PHONY: format check-format lint pre-commit-install pre-commit-run

# Default target
help: ## Zeigt diese Hilfe an
	@echo "AI Media Analysis System - VPS-Optimierte Entwicklungskommandos"
	@echo ""
	@echo "=== QUICK START ==="
	@echo "  make install-dev    - Development-Umgebung einrichten"
	@echo "  make install-test   - Test-Umgebung einrichten"
	@echo "  make quick-start    - Services schnell starten"
	@echo "  make test           - Alle Tests ausführen"
	@echo ""
	@echo "=== INSTALLATION ==="
	@echo "  make install        - Basis-Dependencies (Produktion)"
	@echo "  make install-dev    - Development-Dependencies"
	@echo "  make install-test   - Test-Dependencies"
	@echo "  make install-llm    - LLM Service Dependencies"
	@echo "  make install-vision - Vision Service Dependencies"
	@echo "  make install-cloud  - Cloud Storage Dependencies"
	@echo "  make install-all    - Alle Dependencies (lokal)"
	@echo ""
	@echo "=== DEVELOPMENT ==="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# INSTALLATION UND SETUP
# =============================================================================

install: ## Basis-Installation (Produktion)
	@echo "📦 Installing base dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/base.txt

install-dev: ## Development-Installation
	@echo "🛠️ Installing development dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/development.txt

install-test: ## Test-Installation
	@echo "🧪 Installing test dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/testing.txt

install-llm: ## LLM Service Dependencies
	@echo "🤖 Installing LLM dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/llm.txt

install-vision: ## Vision Service Dependencies
	@echo "👁️ Installing vision dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/vision.txt

install-cloud: ## Cloud Storage Dependencies
	@echo "☁️ Installing cloud dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/cloud.txt

install-all: ## Alle Dependencies (für lokale Entwicklung)
	@echo "📦 Installing all dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/testing.txt
	pip install -r requirements/services/llm.txt
	pip install -r requirements/services/vision.txt
	pip install -r requirements/services/cloud.txt

# Legacy support - weiterhin functional für Backwards Compatibility
install-legacy: ## Legacy installation (alte requirements.txt)
	@echo "📦 Installing legacy dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-ci.txt

dev-setup: install-dev ## Komplette Development-Umgebung
	@echo "🛠️ Setting up complete development environment..."
	@if [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh; \
	else \
		python run_tests.py --check-env; \
	fi

quick-setup: install ## Schnelle minimale Einrichtung
	@echo "⚡ Quick development setup..."
	@if [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh --quick; \
	else \
		@echo "✅ Quick setup completed"; \
	fi

ci-setup: install-test ## Setup für CI/CD-Umgebung
	@echo "🔧 Setting up CI environment..."
	python run_tests.py --check-env

# =============================================================================
# VPS-SPEZIFISCHE ENTWICKLUNG
# =============================================================================

vps-setup: ## VPS-Development-Umgebung vorbereiten
	@echo "🌐 Setting up VPS development environment..."
	@mkdir -p config logs data/{uploads,results,backups}
	@echo "✅ VPS directory structure created"
	@if [ ! -f ".env" ] && [ -f "config/environment.example" ]; then \
		cp config/environment.example .env; \
		echo "⚠️  Please edit .env file for your VPS configuration"; \
	fi

vps-deploy: vps-setup ## VPS-Deployment vorbereiten
	@echo "🚀 Preparing VPS deployment..."
	@echo "Building VPS-optimized Docker images..."
	docker-compose build --parallel redis vector-db data-persistence nginx
	@echo "✅ VPS deployment ready"

vps-test: ## VPS-spezifische Tests ausführen
	@echo "🧪 Running VPS-specific tests..."
	python run_tests.py --unit -m "not gpu and not requires_gpu" -v
	@echo "Testing VPS resource limits..."
	@if command -v docker &> /dev/null; then \
		echo "🐳 Testing Docker resource constraints..."; \
# AI Media Analysis System - VPS-Optimiertes Makefile
# Vereinfacht Test-Ausführung und VPS-Development-Aufgaben

.PHONY: help install test test-unit test-integration test-e2e test-performance
.PHONY: test-coverage test-lint test-security test-docker test-all
.PHONY: format lint clean setup dev-setup ci-setup
.PHONY: run-services stop-services restart-services health-check
.PHONY: vps-setup vps-deploy vps-test logs-all monitor
.PHONY: format check-format lint pre-commit-install pre-commit-run

# Default target
help: ## Zeigt diese Hilfe an
	@echo "AI Media Analysis System - VPS-Optimierte Entwicklungskommandos"
	@echo ""
	@echo "=== QUICK START ==="
	@echo "  make dev-setup      - Komplette Development-Umgebung einrichten"
	@echo "  make quick-start    - Services schnell starten"
	@echo "  make test          - Alle Tests ausführen"
	@echo ""
	@echo "=== DEVELOPMENT ==="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# INSTALLATION UND SETUP
# =============================================================================

install: ## Basis-Installation (Produktion)
	@echo "📦 Installing base dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/base.txt

install-dev: ## Development-Installation
	@echo "🛠️ Installing development dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/development.txt

install-test: ## Test-Installation
	@echo "🧪 Installing test dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/testing.txt

install-llm: ## LLM Service Dependencies
	@echo "🤖 Installing LLM dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/llm.txt

install-vision: ## Vision Service Dependencies
	@echo "👁️ Installing vision dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/vision.txt

install-cloud: ## Cloud Storage Dependencies
	@echo "☁️ Installing cloud dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/services/cloud.txt

install-all: ## Alle Dependencies (für lokale Entwicklung)
	@echo "📦 Installing all dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements/testing.txt
	pip install -r requirements/services/llm.txt
	pip install -r requirements/services/vision.txt
	pip install -r requirements/services/cloud.txt

# Legacy support - weiterhin functional für Backwards Compatibility
install-legacy: ## Legacy installation (alte requirements.txt)
	@echo "📦 Installing legacy dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-ci.txt

dev-setup: install-dev ## Komplette Development-Umgebung
	@echo "🛠️ Setting up complete development environment..."
	@if [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh; \
	else \
		python run_tests.py --check-env; \
	fi

quick-setup: install ## Schnelle minimale Einrichtung
	@echo "⚡ Quick development setup..."
	@if [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh --quick; \
	else \
		@echo "✅ Quick setup completed"; \
	fi

ci-setup: install-test ## Setup für CI/CD-Umgebung
	@echo "🔧 Setting up CI environment..."
	python run_tests.py --check-env

# =============================================================================
# VPS-SPEZIFISCHE ENTWICKLUNG
# =============================================================================

vps-setup: ## VPS-Development-Umgebung vorbereiten
	@echo "🌐 Setting up VPS development environment..."
	@mkdir -p config logs data/{uploads,results,backups}
	@echo "✅ VPS directory structure created"
	@if [ ! -f ".env" ] && [ -f "config/environment.example" ]; then \
		cp config/environment.example .env; \
		echo "⚠️  Please edit .env file for your VPS configuration"; \
	fi

vps-deploy: vps-setup ## VPS-Deployment vorbereiten
	@echo "🚀 Preparing VPS deployment..."
	@echo "Building VPS-optimized Docker images..."
	docker-compose build --parallel redis vector-db data-persistence nginx
	@echo "✅ VPS deployment ready"

vps-test: ## VPS-spezifische Tests ausführen
	@echo "🧪 Running VPS-specific tests..."
	python run_tests.py --unit -m "not gpu and not requires_gpu" -v
	@echo "Testing VPS resource limits..."
	@if command -v docker &> /dev/null; then \
		echo "🐳 Testing Docker resource constraints..."; \
		docker run --rm --memory=2g --cpus=2 python:3.11-slim python -c "print('✅ VPS resource limits OK')"; \
	fi

# =============================================================================
# SERVICES MANAGEMENT
# =============================================================================

quick-start: ## Services schnell für Development starten
	@echo "🚀 Quick starting development services..."
	@if [ -f "scripts/quick-start.sh" ]; then \
		chmod +x scripts/quick-start.sh && ./scripts/quick-start.sh; \
	else \
		$(MAKE) run-core-services; \
	fi

run-services: ## Startet alle Services mit Docker Compose
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 30
	@$(MAKE) health-check

run-core-services: ## Startet nur Core-Services (Redis, Vector-DB, Nginx)
	@echo "🚀 Starting core services for development..."
	docker-compose up -d redis vector-db data-persistence nginx
	@echo "⏳ Waiting for core services..."
	sleep 20
	@$(MAKE) health-check-core

run-ai-services: ## Startet alle AI-Services (CPU-optimiert)
	@echo "🤖 Starting AI services (CPU-optimized)..."
	docker-compose up -d pose_estimation ocr_detection clip_nsfw face_reid whisper_transcriber
	@echo "⏳ Waiting for AI services..."
	sleep 45
	@$(MAKE) health-check-ai

stop-services: ## Stoppt alle Services
	@echo "🛑 Stopping all services..."
	docker-compose down

stop-all: ## Stoppt alle Services und entfernt Volumes
	@echo "🛑 Stopping all services and removing volumes..."
	docker-compose down -v

restart-services: stop-services run-services ## Startet alle Services neu

restart-core: ## Startet nur Core-Services neu
	@echo "🔄 Restarting core services..."
	docker-compose restart redis vector-db data-persistence nginx
	sleep 10
	@$(MAKE) health-check-core

# =============================================================================
# HEALTH CHECKS UND MONITORING
# =============================================================================

health-check: ## Überprüft alle Service-Health
	@echo "🏥 Checking all service health..."
	@$(MAKE) health-check-core
	@$(MAKE) health-check-ai

health-check-core: ## Überprüft Core-Service-Health
	@echo "🏥 Checking core service health..."
	@curl -f http://localhost/health > /dev/null 2>&1 && echo "✅ Nginx healthy" || echo "❌ Nginx not healthy"
	@curl -f http://localhost:8002/health > /dev/null 2>&1 && echo "✅ Vector DB healthy" || echo "❌ Vector DB not healthy"
	@docker exec ai_media_analysis_redis_1 redis-cli ping > /dev/null 2>&1 && echo "✅ Redis healthy" || echo "❌ Redis not healthy"

health-check-ai: ## Überprüft AI-Service-Health
	@echo "🏥 Checking AI service health..."
	@curl -f http://localhost:8001/health > /dev/null 2>&1 && echo "✅ Whisper healthy" || echo "❌ Whisper not healthy"
	@docker ps --filter "name=ai_pose_estimation" --filter "status=running" -q > /dev/null && echo "✅ Pose Estimation running" || echo "❌ Pose Estimation not running"
	@docker ps --filter "name=ai_ocr_detection" --filter "status=running" -q > /dev/null && echo "✅ OCR Detection running" || echo "❌ OCR Detection not running"
	@docker ps --filter "name=ai_clip_nsfw" --filter "status=running" -q > /dev/null && echo "✅ NSFW Detection running" || echo "❌ NSFW Detection not running"
	@docker ps --filter "name=ai_face_reid" --filter "status=running" -q > /dev/null && echo "✅ Face ReID running" || echo "❌ Face ReID not running"

monitor: ## Zeigt kontinuierliches Service-Monitoring
	@echo "📊 Starting continuous service monitoring (Ctrl+C to stop)..."
	@while true; do \
		clear; \
		echo "=== AI Media Analysis - Service Monitor ==="; \
		echo "Time: $$(date)"; \
		echo ""; \
		$(MAKE) health-check 2>/dev/null; \
		echo ""; \
		echo "=== Resource Usage ==="; \
		docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10; \
		sleep 10; \
	done

# =============================================================================
# TESTING
# =============================================================================

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

test-fast: test-unit ## Schnelle Tests (nur Unit Tests)

test-slow: test-integration test-e2e test-performance ## Langsame Tests

test-ci: test-lint test-unit test-integration test-coverage ## Vollständige CI-Tests

# =============================================================================
# CODE-QUALITÄT
# =============================================================================

format: ## Formatiert den Code automatisch mit black und isort
	@echo "🎨 Formatiere Code mit black..."
	python -m black services tests
	@echo "🔧 Sortiere Imports mit isort..."
	python -m isort services tests
	@echo "✅ Code-Formatierung abgeschlossen"

check-format: ## Prüft Code-Formatierung ohne Änderungen
	@echo "🔍 Prüfe black-Formatierung..."
	python -m black --check --diff services tests
	@echo "🔍 Prüfe isort-Formatierung..."
	python -m isort --check-only --diff services tests
	@echo "✅ Formatierungs-Check abgeschlossen"

lint: ## Führt alle Linting-Checks durch
	@echo "🔍 Führe flake8-Check durch..."
	python -m flake8 services tests
	@echo "🔍 Führe mypy-Check durch..."
	python -m mypy services --ignore-missing-imports
	@echo "✅ Linting abgeschlossen"

pre-commit-install: ## Installiert Pre-Commit-Hooks
	@echo "🪝 Installiere Pre-Commit-Hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-Commit-Hooks installiert"

pre-commit-run: ## Führt Pre-Commit-Hooks manuell aus
	@echo "🪝 Führe Pre-Commit-Hooks aus..."
	pre-commit run --all-files
	@echo "✅ Pre-Commit-Hooks ausgeführt"

fix-all: format lint ## Führt automatische Formatierung und Linting durch
	@echo "🔧 Automatische Code-Korrektur abgeschlossen"

test-security: ## Führt Security-Scan aus
	@echo "🔒 Running security scan..."
	python run_tests.py --security

# =============================================================================
# SERVICE-SPEZIFISCHE TESTS
# =============================================================================

test-redis: ## Testet nur Redis Service
	@echo "📮 Testing Redis Service..."
	@docker exec ai_media_analysis_redis_1 redis-cli ping || echo "❌ Redis connection failed"
	@docker exec ai_media_analysis_redis_1 redis-cli info memory | grep used_memory_human || echo "❌ Redis memory check failed"

test-vector-db: ## Testet nur Vector Database
	@echo "🗄️  Testing Vector Database..."
	python -m pytest services/vector_db/tests/ -v

test-whisper-service: ## Testet nur Whisper Service
	@echo "🎤 Testing Whisper Service..."
	@curl -f http://localhost:8001/health > /dev/null 2>&1 && echo "✅ Whisper API responding" || echo "❌ Whisper API not responding"

test-nginx: ## Testet Nginx Configuration
	@echo "🌐 Testing Nginx..."
	@curl -f http://localhost/health > /dev/null 2>&1 && echo "✅ Nginx health endpoint OK" || echo "❌ Nginx health endpoint failed"
	@curl -f http://localhost:8002/health > /dev/null 2>&1 && echo "✅ Nginx proxy to Vector DB OK" || echo "❌ Nginx proxy failed"

# =============================================================================
# LOGGING UND DEBUGGING
# =============================================================================

logs: ## Zeigt alle Docker Service Logs
	docker-compose logs -f

logs-core: ## Zeigt Core Service Logs
	docker-compose logs -f redis vector-db data-persistence nginx

logs-ai: ## Zeigt AI Service Logs
	docker-compose logs -f pose_estimation ocr_detection clip_nsfw face_reid whisper_transcriber

logs-redis: ## Zeigt nur Redis Logs
	docker-compose logs -f redis

logs-vector: ## Zeigt nur Vector DB Logs
	docker-compose logs -f vector-db

logs-whisper: ## Zeigt nur Whisper Logs
	docker-compose logs -f whisper_transcriber

logs-nginx: ## Zeigt nur Nginx Logs
	docker-compose logs -f nginx

logs-all: ## Zeigt alle Logs mit Timestamps
	@echo "📜 Showing all service logs..."
	docker-compose logs -f --timestamps

# =============================================================================
# ENTWICKLUNGSTOOLS
# =============================================================================

clean: ## Bereinigt temporäre Dateien
	@echo "🧽 Cleaning up..."
	python run_tests.py --cleanup
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
	@echo "✅ Cleanup completed"

clean-docker: ## Bereinigt Docker-Artefakte
	@echo "🐳 Cleaning Docker artifacts..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f
	@echo "✅ Docker cleanup completed"

clean-all: clean clean-docker ## Vollständige Bereinigung

reset-dev: clean-all ## Reset komplette Development-Umgebung
	@echo "🔄 Resetting development environment..."
	@if [ -f "scripts/reset-dev.sh" ]; then \
		chmod +x scripts/reset-dev.sh && ./scripts/reset-dev.sh; \
	else \
		rm -rf data/uploads/* data/results/* logs/* 2>/dev/null || true; \
		echo "✅ Development environment reset"; \
	fi

# =============================================================================
# UTILITY-TARGETS
# =============================================================================

setup: dev-setup ## Alias für dev-setup

check-deps: ## Überprüft Abhängigkeiten auf Updates
	@echo "🔍 Checking for dependency updates..."
	pip list --outdated

install-dev-tools: ## Installiert zusätzliche Entwicklungstools
	@echo "🛠️  Installing development tools..."
	pip install bandit safety pre-commit pytest-benchmark

update-deps: ## Aktualisiert Abhängigkeiten
	@echo "⬆️  Updating dependencies..."
	pip install --upgrade -r requirements.txt
	pip install --upgrade -r requirements-ci.txt

# =============================================================================
# PERFORMANCE UND BENCHMARKS
# =============================================================================

benchmark: ## Führt Performance-Benchmarks aus
	@echo "⚡ Running performance benchmarks..."
	python run_tests.py --performance -v
	@echo "📊 Benchmark results saved to benchmarks/"

stress-test: ## Führt Stress-Tests aus
	@echo "💪 Running stress tests..."
	@echo "Testing Redis under load..."
	@for i in {1..100}; do docker exec ai_media_analysis_redis_1 redis-cli set "test_$$i" "value_$$i" > /dev/null; done
	@echo "✅ Redis stress test completed"

load-test: ## Führt Load-Tests aus
	@echo "📈 Running load tests..."
	@echo "Note: This requires services to be running (make run-services)"
	@ab -n 100 -c 10 http://localhost/health || echo "❌ Apache Bench (ab) not installed"

# =============================================================================
# DOKUMENTATION
# =============================================================================

docs: ## Generiert Dokumentation
	@echo "📚 Generating documentation..."
	@echo "TODO: Add documentation generation"

docs-serve: ## Startet lokalen Dokumentations-Server
	@echo "📖 Starting documentation server..."
	@echo "TODO: Add documentation server"

# =============================================================================
# PRODUCTION-VORBEREITUNG
# =============================================================================

build-production: ## Buildet Production-Docker-Images
	@echo "🏭 Building production Docker images..."
	docker-compose -f docker-compose.prod.yml build || echo "⚠️  docker-compose.prod.yml not found"

deploy-staging: ## Deployed zu Staging-Umgebung
	@echo "🎭 Deploying to staging..."
	@echo "TODO: Add staging deployment"

deploy-production: ## Deployed zu Production-Umgebung
	@echo "🚀 Deploying to production..."
	@echo "TODO: Add production deployment"
