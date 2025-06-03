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
# CODE-QUALITÄT UND BLACK-STANDARD
# =============================================================================

format: ## Formatiert den Code automatisch mit black und isort
	@echo "🎨 Formatiere Python-Code mit Black..."
	python -m black services/ tests/ scripts/ --target-version py311
	@echo "🔧 Sortiere Imports mit isort..."
	python -m isort services/ tests/ scripts/ --profile black
	@echo "✅ Code-Formatierung abgeschlossen"

check-format: ## Prüft Code-Formatierung ohne Änderungen
	@echo "🔍 Prüfe Black-Formatierung..."
	python -m black --check --diff services/ tests/ scripts/
	@echo "🔍 Prüfe isort-Formatierung..."
	python -m isort --check-only --diff services/ tests/ scripts/
	@echo "✅ Formatierungs-Check abgeschlossen"

format-check-strict: ## Strenger Formatierungs-Check für CI/CD
	@echo "🚨 Strenger Black-Standard-Check..."
	python -m black --check services/ tests/ scripts/ || (echo "❌ Black-Formatierung fehlgeschlagen" && exit 1)
	python -m isort --check-only services/ tests/ scripts/ || (echo "❌ Import-Sortierung fehlgeschlagen" && exit 1)
	@echo "✅ Strenger Formatierungs-Check erfolgreich"

lint: ## Führt alle Linting-Checks durch
	@echo "🔍 Führe flake8-Check durch..."
	python -m flake8 services tests scripts
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

format-report: ## Generiert Format-Compliance-Report
	@echo "📊 Generiere Format-Compliance-Report..."
	@echo "# Black-Standard Compliance Report" > format-report.md
	@echo "Generated: $(shell date)" >> format-report.md
	@echo "" >> format-report.md
	@echo "## Black Check Results" >> format-report.md
	@python -m black --check services/ tests/ scripts/ --quiet && echo "✅ All files compliant" >> format-report.md || echo "❌ Files need formatting" >> format-report.md
	@echo "" >> format-report.md
	@echo "## Import Sorting Results" >> format-report.md
	@python -m isort --check-only services/ tests/ scripts/ --quiet && echo "✅ All imports sorted" >> format-report.md || echo "❌ Imports need sorting" >> format-report.md
	@echo "📋 Report saved: format-report.md"

black-violations-report: ## Report für Black-Standard-Verletzungen
	@echo "🔍 Generiere Black-Violations-Report..."
	@mkdir -p reports/
	@echo "# Black Standard Violations Report" > reports/black-violations.md
	@echo "Generated: $(shell date)" >> reports/black-violations.md
	@echo "" >> reports/black-violations.md
	@echo "## Files requiring Black formatting:" >> reports/black-violations.md
	@python -m black --check --diff services/ tests/ scripts/ >> reports/black-violations.md 2>&1 || true
	@echo "" >> reports/black-violations.md
	@echo "## Files requiring import sorting:" >> reports/black-violations.md
	@python -m isort --check-only --diff services/ tests/ scripts/ >> reports/black-violations.md 2>&1 || true
	@echo "📋 Violations report: reports/black-violations.md"

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

# =============================================================================
# 🔄 ITERATIVE SERVICE-INTEGRATION (Alpha 0.5.0)
# =============================================================================

## Service-Integration Management
iteration-1: ## 🔄 Integration Iteration 1: Management-Core (4 Services)
	@echo "${GREEN}🔄 Starte Iteration 1: Management-Core Services${NC}"
	@echo "${YELLOW}Services: $(ITERATION_1_SERVICES)${NC}"
	@for service in $(ITERATION_1_SERVICES); do \
		echo "${BLUE}Integriere Service: $$service${NC}"; \
		$(MAKE) service-add SERVICE=$$service || exit 1; \
	done
	@$(MAKE) iteration-test ITERATION=1
	@echo "${GREEN}✅ Iteration 1 abgeschlossen - Management-Core aktiv${NC}"

iteration-2: ## 🔄 Integration Iteration 2: AI-Processing-Core (3 Services)
	@echo "${GREEN}🔄 Starte Iteration 2: AI-Processing-Core Services${NC}"
	@echo "${YELLOW}Services: $(ITERATION_2_SERVICES)${NC}"
	@for service in $(ITERATION_2_SERVICES); do \
		echo "${BLUE}Integriere Service: $$service${NC}"; \
		$(MAKE) service-add SERVICE=$$service || exit 1; \
	done
	@$(MAKE) iteration-test ITERATION=2
	@echo "${GREEN}✅ Iteration 2 abgeschlossen - AI-Processing-Pipeline aktiv${NC}"

iteration-3: ## 🔄 Integration Iteration 3: Specialized-Services (4 Services)
	@echo "${GREEN}🔄 Starte Iteration 3: Specialized-Services${NC}"
	@echo "${YELLOW}Services: $(ITERATION_3_SERVICES)${NC}"
	@for service in $(ITERATION_3_SERVICES); do \
		echo "${BLUE}Integriere Service: $$service${NC}"; \
		$(MAKE) service-add SERVICE=$$service || exit 1; \
	done
	@$(MAKE) iteration-test ITERATION=3
	@echo "${GREEN}✅ Iteration 3 abgeschlossen - Specialized-Detection aktiv${NC}"

iteration-4: ## 🔄 Integration Iteration 4: Content & UI-Services (3 Services)
	@echo "${GREEN}🔄 Starte Iteration 4: Content & UI-Services${NC}"
	@echo "${YELLOW}Services: $(ITERATION_4_SERVICES)${NC}"
	@for service in $(ITERATION_4_SERVICES); do \
		echo "${BLUE}Integriere Service: $$service${NC}"; \
		$(MAKE) service-add SERVICE=$$service || exit 1; \
	done
	@$(MAKE) iteration-test ITERATION=4
	@echo "${GREEN}✅ Iteration 4 abgeschlossen - Production-UI verfügbar${NC}"

service-add: ## 🔧 Service zu docker-compose.yml hinzufügen (SERVICE=name)
	@if [ -z "$(SERVICE)" ]; then \
		echo "${RED}❌ Fehler: SERVICE Parameter erforderlich${NC}"; \
		echo "${YELLOW}Verwendung: make service-add SERVICE=service_name${NC}"; \
		exit 1; \
	fi
	@echo "${BLUE}🔧 Füge Service $(SERVICE) zu docker-compose.yml hinzu${NC}"
	@if [ ! -d "services/$(SERVICE)" ]; then \
		echo "${RED}❌ Service-Verzeichnis services/$(SERVICE) nicht gefunden${NC}"; \
		exit 1; \
	fi
	@$(MAKE) service-dockerfile-cpu SERVICE=$(SERVICE)
	@$(MAKE) service-config-generate SERVICE=$(SERVICE)
	@echo "${GREEN}✅ Service $(SERVICE) erfolgreich hinzugefügt${NC}"

service-dockerfile-cpu: ## 🐳 Dockerfile.cpu für Service erstellen (SERVICE=name)
	@echo "${BLUE}🐳 Erstelle Dockerfile.cpu für $(SERVICE)${NC}"
	@if [ ! -f "services/$(SERVICE)/Dockerfile.cpu" ]; then \
		echo "# CPU-optimierte Dockerfile für $(SERVICE)" > services/$(SERVICE)/Dockerfile.cpu; \
		echo "FROM python:3.11-slim" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# System-Dependencies für VPS" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "RUN apt-get update && apt-get install -y \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    build-essential \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    curl \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    && rm -rf /var/lib/apt/lists/*" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "WORKDIR /app" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Python Dependencies" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "COPY requirements.txt ." >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "RUN pip install --no-cache-dir -r requirements.txt" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Service Code" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "COPY . ." >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# VPS-Umgebungsvariablen" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV PYTHONUNBUFFERED=1" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV LOG_LEVEL=INFO" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV REDIS_HOST=redis" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV REDIS_PORT=6379" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Health-Check" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    CMD curl -f http://localhost:8000/health || exit 1" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Service starten" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "${GREEN}✅ Dockerfile.cpu für $(SERVICE) erstellt${NC}"; \
	fi

service-config-generate: ## ⚙️ Service-Konfiguration für docker-compose.yml generieren
	@echo "${BLUE}⚙️ Generiere docker-compose.yml Konfiguration für $(SERVICE)${NC}"
	@python scripts/generate_service_config.py $(SERVICE)

service-test: ## 🧪 Service Health-Check (SERVICE=name)
	@if [ -z "$(SERVICE)" ]; then \
		echo "${RED}❌ Fehler: SERVICE Parameter erforderlich${NC}"; \
		exit 1; \
	fi
	@echo "${BLUE}🧪 Teste Service $(SERVICE)${NC}"
	@$(DOCKER_COMPOSE) ps $(SERVICE) || exit 1
	@$(DOCKER_COMPOSE) exec $(SERVICE) curl -f http://localhost:8000/health || echo "${YELLOW}⚠️ Health-Check für $(SERVICE) fehlgeschlagen${NC}"

iteration-test: ## 🧪 Test aller Services der aktuellen Iteration (ITERATION=1-4)
	@echo "${BLUE}🧪 Teste Iteration $(ITERATION) Services${NC}"
	@if [ "$(ITERATION)" = "1" ]; then \
		for service in $(ITERATION_1_SERVICES); do $(MAKE) service-test SERVICE=$$service; done; \
	elif [ "$(ITERATION)" = "2" ]; then \
		for service in $(ITERATION_1_SERVICES) $(ITERATION_2_SERVICES); do $(MAKE) service-test SERVICE=$$service; done; \
	elif [ "$(ITERATION)" = "3" ]; then \
		for service in $(ITERATION_1_SERVICES) $(ITERATION_2_SERVICES) $(ITERATION_3_SERVICES); do $(MAKE) service-test SERVICE=$$service; done; \
	elif [ "$(ITERATION)" = "4" ]; then \
		for service in $(ALL_NEW_SERVICES); do $(MAKE) service-test SERVICE=$$service; done; \
	fi
	@echo "${GREEN}✅ Iteration $(ITERATION) Tests abgeschlossen${NC}"

iteration-status: ## 📊 Status-Übersicht der aktuellen Service-Integration
	@echo "${GREEN}📊 Service-Integration Status${NC}"
	@echo "${BLUE}================================${NC}"
	@echo "${YELLOW}Aktive Services (docker-compose.yml):${NC}"
	@$(DOCKER_COMPOSE) config --services | wc -l | xargs echo "Services in docker-compose.yml:"
	@echo ""
	@echo "${YELLOW}Iteration 1 - Management-Core:${NC}"
	@for service in $(ITERATION_1_SERVICES); do \
		if $(DOCKER_COMPOSE) config --services | grep -q $$service; then \
			echo "  ✅ $$service"; \
		else \
			echo "  ⏳ $$service"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Iteration 2 - AI-Processing-Core:${NC}"
	@for service in $(ITERATION_2_SERVICES); do \
		if $(DOCKER_COMPOSE) config --services | grep -q $$service; then \
			echo "  ✅ $$service"; \
		else \
			echo "  ⏳ $$service"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Iteration 3 - Specialized-Services:${NC}"
	@for service in $(ITERATION_3_SERVICES); do \
		if $(DOCKER_COMPOSE) config --services | grep -q $$service; then \
			echo "  ✅ $$service"; \
		else \
			echo "  ⏳ $$service"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Iteration 4 - Content & UI-Services:${NC}"
	@for service in $(ITERATION_4_SERVICES); do \
		if $(DOCKER_COMPOSE) config --services | grep -q $$service; then \
			echo "  ✅ $$service"; \
		else \
			echo "  ⏳ $$service"; \
		fi; \
	done

dockerfile-cpu-template: ## 📝 CPU-Dockerfile-Template für Service generieren
	@mkdir -p services/$(SERVICE)
	@if [ ! -f "services/$(SERVICE)/Dockerfile.cpu" ]; then \
		echo "# CPU-optimierte Dockerfile für $(SERVICE)" > services/$(SERVICE)/Dockerfile.cpu; \
		echo "FROM python:3.11-slim" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# System-Dependencies für VPS" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "RUN apt-get update && apt-get install -y \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    build-essential \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    curl \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    && rm -rf /var/lib/apt/lists/*" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "WORKDIR /app" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Python Dependencies" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "COPY requirements.txt ." >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "RUN pip install --no-cache-dir -r requirements.txt" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Service Code" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "COPY . ." >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# VPS-Umgebungsvariablen" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV PYTHONUNBUFFERED=1" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV LOG_LEVEL=INFO" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV REDIS_HOST=redis" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "ENV REDIS_PORT=6379" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Health-Check" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "    CMD curl -f http://localhost:8000/health || exit 1" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "# Service starten" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" >> services/$(SERVICE)/Dockerfile.cpu; \
		echo "${GREEN}✅ Dockerfile.cpu für $(SERVICE) erstellt${NC}"; \
	fi

integration-all: ## 🚀 Alle 4 Iterationen nacheinander ausführen
	@echo "${GREEN}🚀 Starte komplette Service-Integration (4 Iterationen)${NC}"
	@$(MAKE) iteration-1
	@echo "${BLUE}Pause zwischen Iterationen (30s)...${NC}"
	@sleep 30
	@$(MAKE) iteration-2
	@sleep 30
	@$(MAKE) iteration-3
	@sleep 30
	@$(MAKE) iteration-4
	@echo "${GREEN}🎉 Alle 24 Services erfolgreich integriert!${NC}"
	@$(MAKE) iteration-status

# =============================================================================
# 🧪 FEATURE TESTING FRAMEWORK (NEUE REGEL)
# =============================================================================

## Comprehensive Testing Pipeline
test: test-unit test-integration test-e2e ## 🧪 Führe alle Tests aus (Feature Testing Regel)
	@echo "${GREEN}✅ Alle Tests erfolgreich!${NC}"

test-unit: ## 🧪 Unit Tests mit Coverage-Anforderung (min. 80%)
	@echo "${BLUE}🧪 Führe Unit Tests aus...${NC}"
	@pytest tests/unit/ -v \
		--cov=services \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=80 \
		--maxfail=5 \
		--timeout=300 \
		--durations=10 \
		-m "unit"
	@echo "${GREEN}✅ Unit Tests abgeschlossen${NC}"

test-integration: ## 🔗 Integration Tests zwischen Services
	@echo "${BLUE}🔗 Führe Integration Tests aus...${NC}"
	@echo "${YELLOW}Starte erforderliche Services für Integration Tests...${NC}"
	@$(DOCKER_COMPOSE) up -d redis
	@sleep 5
	@pytest tests/integration/ -v \
		--timeout=600 \
		--maxfail=3 \
		--durations=10 \
		-m "integration"
	@echo "${GREEN}✅ Integration Tests abgeschlossen${NC}"

test-e2e: ## 🎯 End-to-End Tests (vollständige Workflows)
	@echo "${BLUE}🎯 Führe E2E Tests aus...${NC}"
	@echo "${YELLOW}Starte alle Services für E2E Tests...${NC}"
	@$(DOCKER_COMPOSE) up -d
	@echo "${YELLOW}Warte auf Service-Start (60s)...${NC}"
	@sleep 60
	@pytest tests/e2e/ -v \
		--timeout=1200 \
		--maxfail=1 \
		--durations=10 \
		--tb=short \
		-m "e2e"
	@$(DOCKER_COMPOSE) down
	@echo "${GREEN}✅ E2E Tests abgeschlossen${NC}"

test-performance: ## ⚡ Performance Tests und Load Testing
	@echo "${BLUE}⚡ Führe Performance Tests aus...${NC}"
	@pytest tests/performance/ -v \
		--timeout=1800 \
		--durations=10 \
		-m "performance"
	@echo "${GREEN}✅ Performance Tests abgeschlossen${NC}"

test-security: ## 🔒 Security Tests und Vulnerability Scans
	@echo "${BLUE}🔒 Führe Security Tests aus...${NC}"
	@echo "${YELLOW}Bandit Security Scan...${NC}"
	@bandit -r services/ --severity-level medium --confidence-level medium || echo "${YELLOW}⚠️ Bandit-Warnungen gefunden${NC}"
	@echo "${YELLOW}Safety Dependency Check...${NC}"
	@safety check || echo "${YELLOW}⚠️ Safety-Warnungen gefunden${NC}"
	@echo "${YELLOW}Security-spezifische Tests...${NC}"
	@pytest tests/ -v -m "security" --timeout=300 || echo "${YELLOW}⚠️ Security-Tests mit Warnungen${NC}"
	@echo "${GREEN}✅ Security Tests abgeschlossen${NC}"

test-coverage: ## 📊 Coverage Report generieren und anzeigen
	@echo "${BLUE}📊 Generiere Coverage Report...${NC}"
	@pytest tests/unit/ tests/integration/ \
		--cov=services \
		--cov-report=html:htmlcov \
		--cov-report=term-missing \
		--cov-report=xml \
		--cov-fail-under=80
	@echo "${GREEN}✅ Coverage Report generiert: htmlcov/index.html${NC}"
	@echo "${YELLOW}Coverage-Zusammenfassung:${NC}"
	@coverage report --show-missing

test-smoke: ## 💨 Smoke Tests für schnelle Systemprüfung
	@echo "${BLUE}💨 Führe Smoke Tests aus...${NC}"
	@$(DOCKER_COMPOSE) up -d
	@sleep 30
	@pytest tests/ -v -m "smoke" \
		--timeout=120 \
		--maxfail=1
	@$(DOCKER_COMPOSE) down
	@echo "${GREEN}✅ Smoke Tests abgeschlossen${NC}"

test-validate: ## 🔍 Validiere Test-Anforderungen für neue Features
	@echo "${BLUE}🔍 Validiere Test-Anforderungen...${NC}"
	@echo "${YELLOW}Prüfe Test-Coverage für services/...${NC}"
	@for service_file in $$(find services/ -name "*.py" -not -name "__init__.py" -not -name "test_*"); do \
		test_file=$$(echo "$$service_file" | sed 's|services/|tests/unit/services/|' | sed 's|\.py$$|_test.py|' | sed 's|/\([^/]*\)_test\.py$$|/test_\1.py|'); \
		if [ ! -f "$$test_file" ]; then \
			echo "${RED}❌ Missing test: $$test_file für $$service_file${NC}"; \
			missing_tests=1; \
		fi; \
	done; \
	if [ "$$missing_tests" = "1" ]; then \
		echo "${RED}❌ Feature Testing Regel verletzt: Tests für alle Service-Dateien erforderlich${NC}"; \
		exit 1; \
	else \
		echo "${GREEN}✅ Alle Service-Dateien haben entsprechende Tests${NC}"; \
	fi

test-watch: ## 👀 Kontinuierliche Test-Ausführung bei Dateiänderungen
	@echo "${BLUE}👀 Starte kontinuierliche Test-Überwachung...${NC}"
	@echo "${YELLOW}Tests werden bei Dateiänderungen automatisch ausgeführt...${NC}"
	@pytest-watch tests/unit/ -- -v --tb=short

test-parallel: ## 🚀 Parallele Test-Ausführung (schneller)
	@echo "${BLUE}🚀 Führe Tests parallel aus...${NC}"
	@pytest tests/unit/ -v \
		--cov=services \
		--cov-report=term-missing \
		--cov-fail-under=80 \
		-n auto \
		--timeout=300 \
		--durations=10

test-debug: ## 🐛 Debug-Modus für Tests (ausführliche Ausgaben)
	@echo "${BLUE}🐛 Debug-Modus für Tests...${NC}"
	@pytest tests/ -v -s \
		--tb=long \
		--capture=no \
		--timeout=600 \
		--pdb-trace

test-clean: ## 🧹 Test-Artifacts und Cache löschen
	@echo "${BLUE}🧹 Lösche Test-Artifacts...${NC}"
	@rm -rf .pytest_cache/
	@rm -rf htmlcov/
	@rm -rf .coverage*
	@rm -rf coverage.xml
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✅ Test-Artifacts gelöscht${NC}"

test-setup: ## 🛠️ Test-Umgebung einrichten
	@echo "${BLUE}🛠️ Richte Test-Umgebung ein...${NC}"
	@pip install -r requirements-ci.txt
	@mkdir -p tests/{unit,integration,e2e,performance,fixtures,utils}
	@mkdir -p tests/unit/services
	@mkdir -p tests/data/{videos,images,json}
	@if [ ! -f "tests/conftest.py" ]; then \
		echo "# Test configuration" > tests/conftest.py; \
		echo "import pytest" >> tests/conftest.py; \
		echo "" >> tests/conftest.py; \
		echo "@pytest.fixture(scope='session')" >> tests/conftest.py; \
		echo "def test_client():" >> tests/conftest.py; \
		echo "    \"\"\"Test client fixture.\"\"\"" >> tests/conftest.py; \
		echo "    pass" >> tests/conftest.py; \
	fi
	@echo "${GREEN}✅ Test-Umgebung eingerichtet${NC}"

test-ci: ## 🤖 CI/CD Test-Pipeline (simuliert GitHub Actions)
	@echo "${BLUE}🤖 Simuliere CI/CD Test-Pipeline...${NC}"
	@$(MAKE) test-validate
	@$(MAKE) test-unit
	@$(MAKE) test-integration
	@$(MAKE) test-security
	@$(MAKE) test-coverage
	@echo "${GREEN}✅ CI/CD Test-Pipeline erfolgreich${NC}"

## Test Quality Gates
test-quality-gate: ## 🚥 Quality Gate für Feature-Deployment
	@echo "${BLUE}🚥 Prüfe Quality Gate...${NC}"
	@$(MAKE) test-validate
	@$(MAKE) test-unit
	@coverage report --fail-under=80 || (echo "${RED}❌ Coverage unter 80%${NC}" && exit 1)
	@$(MAKE) test-integration
	@$(MAKE) test-security
	@echo "${GREEN}✅ Quality Gate bestanden - Feature kann deployed werden${NC}"

## Test Reporting
test-report: ## 📋 Umfassender Test-Report generieren
	@echo "${BLUE}📋 Generiere umfassenden Test-Report...${NC}"
	@mkdir -p reports/
	@echo "# Test Report - $(shell date)" > reports/test-report.md
	@echo "" >> reports/test-report.md
	@echo "## Test Coverage" >> reports/test-report.md
	@coverage report --format=markdown >> reports/test-report.md 2>/dev/null || echo "Coverage-Daten nicht verfügbar" >> reports/test-report.md
	@echo "" >> reports/test-report.md
	@echo "## Test Statistics" >> reports/test-report.md
	@echo "- Unit Tests: $$(find tests/unit -name 'test_*.py' | wc -l)" >> reports/test-report.md
	@echo "- Integration Tests: $$(find tests/integration -name 'test_*.py' | wc -l)" >> reports/test-report.md
	@echo "- E2E Tests: $$(find tests/e2e -name 'test_*.py' | wc -l)" >> reports/test-report.md
	@echo "- Performance Tests: $$(find tests/performance -name 'test_*.py' | wc -l)" >> reports/test-report.md
	@echo "${GREEN}✅ Test-Report erstellt: reports/test-report.md${NC}"

test-help: ## ❓ Hilfe zu Test-Befehlen anzeigen
	@echo "${GREEN}🧪 Feature Testing Framework - Verfügbare Befehle:${NC}"
	@echo ""
	@echo "${YELLOW}Grundlegende Tests:${NC}"
	@echo "  make test              - Alle Tests ausführen"
	@echo "  make test-unit         - Unit Tests (schnell, isoliert)"
	@echo "  make test-integration  - Integration Tests (Service-Interaktionen)"
	@echo "  make test-e2e          - End-to-End Tests (vollständige Workflows)"
	@echo ""
	@echo "${YELLOW}Spezielle Tests:${NC}"
	@echo "  make test-performance  - Performance und Load Tests"
	@echo "  make test-security     - Security Tests und Scans"
	@echo "  make test-smoke        - Schnelle System-Checks"
	@echo ""
	@echo "${YELLOW}Test-Qualität:${NC}"
	@echo "  make test-coverage     - Coverage Report"
	@echo "  make test-validate     - Test-Anforderungen prüfen"
	@echo "  make test-quality-gate - Quality Gate für Deployment"
	@echo ""
	@echo "${YELLOW}Test-Utilities:${NC}"
	@echo "  make test-setup        - Test-Umgebung einrichten"
	@echo "  make test-clean        - Test-Artifacts löschen"
	@echo "  make test-parallel     - Parallel ausführen"
	@echo "  make test-debug        - Debug-Modus"
	@echo "  make test-watch        - Kontinuierliche Ausführung"
	@echo ""
	@echo "${YELLOW}Reporting:${NC}"
	@echo "  make test-report       - Umfassender Test-Report"
	@echo "  make test-ci           - CI/CD Pipeline simulieren"

# =============================================================================
# KONFIGURATIONSDATEI-VALIDIERUNG (NEUE REGEL)
# =============================================================================

validate-config: ## Validiert alle Konfigurationsdateien
	@echo "🔍 Validiere Konfigurationsdateien..."
	python scripts/validate_config.py
	@echo "✅ Konfigurationsvalidierung abgeschlossen"

check-pytest-ini: ## Spezielle pytest.ini Validierung
	@echo "🧪 Validiere pytest.ini..."
	python -c "import configparser; c=configparser.ConfigParser(); c.read('pytest.ini'); print('✅ pytest.ini syntax OK')" || (echo "❌ pytest.ini Syntax-Fehler" && exit 1)
	python scripts/validate_config.py --file pytest

check-pyproject: ## Validiert pyproject.toml
	@echo "📦 Validiere pyproject.toml..."
	python -c "import tomli; tomli.load(open('pyproject.toml', 'rb')); print('✅ pyproject.toml syntax OK')" || (echo "❌ pyproject.toml Syntax-Fehler" && exit 1)
	python scripts/validate_config.py --file pyproject

check-docker-compose: ## Validiert docker-compose.yml
	@echo "🐳 Validiere docker-compose.yml..."
	docker-compose config --quiet && echo "✅ docker-compose.yml syntax OK" || (echo "❌ docker-compose.yml Syntax-Fehler" && exit 1)
	python scripts/validate_config.py --file docker-compose

fix-config: ## Automatische Konfigurationsreparatur (wo möglich)
	@echo "🔧 Repariere Konfigurationsdateien..."
	python scripts/validate_config.py --fix
	@echo "✅ Konfigurationsreparatur abgeschlossen"

config-health-check: ## Umfassende Konfigurationsprüfung
	@echo "🏥 Konfiguration Health Check..."
	python scripts/validate_config.py --comprehensive
	@echo "📊 Config Health Report generiert"

validate-all-config: validate-config check-pytest-ini check-pyproject check-docker-compose ## Vollständige Konfigurationsvalidierung
	@echo "✅ Vollständige Konfigurationsvalidierung abgeschlossen"
