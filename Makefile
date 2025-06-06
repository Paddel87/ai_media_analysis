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
# TESTING - siehe Feature Testing Regel weiter unten
# =============================================================================

# Test-Targets sind in der Feature Testing Regel Sektion definiert (Zeile ~700)
# Um Duplikate zu vermeiden, siehe die umfassenden Test-Targets weiter unten

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

# test-security ist in der Feature Testing Regel Sektion definiert (siehe weiter unten)

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

dockerfile-cpu-template: service-dockerfile-cpu ## 📝 CPU-Dockerfile-Template (Alias für service-dockerfile-cpu)

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

# =============================================================================
# LINTER-COMPLIANCE-REGEL (NEUE REGEL)
# =============================================================================

## Comprehensive Linter Compliance
check-compliance: ## 🔍 Vollständige Linter-Compliance-Prüfung
	@echo "${BLUE}🔍 Führe vollständige Linter-Compliance-Prüfung durch...${NC}"
	python scripts/linter_compliance.py
	@echo "${GREEN}✅ Linter-Compliance-Check abgeschlossen${NC}"

check-compliance-critical: ## 🎯 Nur kritische Compliance-Checks
	@echo "${BLUE}🎯 Führe kritische Linter-Checks durch...${NC}"
	python scripts/linter_compliance.py --critical-only
	@echo "${GREEN}✅ Kritische Compliance-Checks abgeschlossen${NC}"

fix-compliance: ## 🔧 Automatische Compliance-Reparatur
	@echo "${BLUE}🔧 Führe automatische Compliance-Reparatur durch...${NC}"
	python scripts/linter_compliance.py --fix
	@echo "${GREEN}✅ Automatische Reparatur abgeschlossen${NC}"

compliance-report: ## 📊 Compliance-Report generieren
	@echo "${BLUE}📊 Generiere Compliance-Report...${NC}"
	python scripts/linter_compliance.py --report-only
	@echo "${GREEN}✅ Compliance-Report generiert${NC}"

lint-help: ## ❓ Linter-Compliance Hilfe anzeigen
	@echo "${GREEN}🔍 Linter-Compliance-Regel - Verfügbare Befehle:${NC}"
	@echo ""
	@echo "${YELLOW}Compliance Checks:${NC}"
	@echo "  make check-compliance         - Vollständige Compliance-Prüfung"
	@echo "  make check-compliance-critical- Nur kritische Checks"
	@echo "  make fix-compliance           - Automatische Reparatur"
	@echo "  make compliance-report        - Report generieren"
	@echo ""
	@echo "${YELLOW}Einzelne Tools:${NC}"
	@echo "  make format                   - Black + isort Formatierung"
	@echo "  make check-format             - Formatierung prüfen"
	@echo "  make lint                     - flake8 + mypy Checks"
	@echo "  make validate-config          - Konfigurationsdatei-Validierung"
	@echo ""
	@echo "${YELLOW}Compliance Levels:${NC}"
	@echo "  🎯 MINIMUM    - Kritische Checks bestanden"
	@echo "  ⚠️ RECOMMENDED - + Security/Type Checks"
	@echo "  🎉 EXCELLENCE - Alle Checks perfekt"
	@echo ""
	@echo "${YELLOW}CI/CD Integration:${NC}"
	@echo "  - GitHub Actions: .github/workflows/linter-compliance.yml"
	@echo "  - Pre-commit Hooks: make pre-commit-install"
	@echo "  - Automatische Formatierung bei jedem Commit"

compliance-help: lint-help ## ❓ Alias für lint-help

format-help: ## ❓ Formatierungs-Hilfe anzeigen
	@echo "${GREEN}🎨 Code-Formatierung - Verfügbare Befehle:${NC}"
	@echo ""
	@echo "${YELLOW}Automatische Formatierung:${NC}"
	@echo "  make format                   - Black + isort Formatierung"
	@echo "  make fix-all                  - Format + Lint + Config Fix"
	@echo ""
	@echo "${YELLOW}Formatierungs-Checks:${NC}"
	@echo "  make check-format             - Formatierung prüfen"
	@echo "  make format-check-strict      - Strenger Check für CI/CD"
	@echo ""
	@echo "${YELLOW}Reports:${NC}"
	@echo "  make format-report            - Format-Compliance-Report"
	@echo "  make black-violations-report  - Black-Violations-Report"
	@echo ""
	@echo "${YELLOW}Konfiguration:${NC}"
	@echo "  - pyproject.toml: [tool.black] und [tool.isort]"
	@echo "  - setup.cfg: [flake8] Konfiguration"
	@echo "  - Line length: 88 Zeichen (Black Standard)"

fix-imports: ## 🔧 Nur Import-Sortierung reparieren
	@echo "${BLUE}🔧 Repariere Import-Sortierung...${NC}"
	python -m isort services/ tests/ scripts/ --profile black
	@echo "${GREEN}✅ Import-Sortierung abgeschlossen${NC}"

fix-config: ## 🏗️ Nur Konfigurationsfehler reparieren
	@echo "${BLUE}🏗️ Repariere Konfigurationsfehler...${NC}"
	python scripts/validate_config.py --fix
	@echo "${GREEN}✅ Konfigurationsreparatur abgeschlossen${NC}"

## Security und Quality Gates
security-gate: ## 🔒 Security Gate für CI/CD
	@echo "${BLUE}🔒 Führe Security Gate durch...${NC}"
	@python -m bandit -r services/ --severity-level medium --confidence-level medium
	@python -m safety check
	@echo "${GREEN}✅ Security Gate bestanden${NC}"

quality-gate: ## 📋 Quality Gate für CI/CD
	@echo "${BLUE}📋 Führe Quality Gate durch...${NC}"
	@$(MAKE) check-format
	@$(MAKE) lint
	@$(MAKE) validate-config
	@echo "${GREEN}✅ Quality Gate bestanden${NC}"

compliance-gate: quality-gate security-gate ## 🚥 Vollständiges Compliance Gate
	@echo "${GREEN}🚥 Compliance Gate erfolgreich bestanden!${NC}"

## Daily Compliance Tasks
daily-compliance: ## 📅 Tägliche Compliance-Prüfung
	@echo "${BLUE}📅 Führe tägliche Compliance-Prüfung durch...${NC}"
	@$(MAKE) fix-compliance
	@$(MAKE) check-compliance
	@$(MAKE) compliance-report
	@echo "${GREEN}✅ Tägliche Compliance-Prüfung abgeschlossen${NC}"

pre-merge-check: ## 🔀 Pre-Merge Compliance Check
	@echo "${BLUE}🔀 Führe Pre-Merge Compliance Check durch...${NC}"
	@$(MAKE) check-compliance-critical
	@$(MAKE) test-unit
	@$(MAKE) security-gate
	@echo "${GREEN}✅ Pre-Merge Check bestanden - Ready to merge!${NC}"

release-compliance: ## 🚀 Release Compliance Audit
	@echo "${BLUE}🚀 Führe Release Compliance Audit durch...${NC}"
	@$(MAKE) check-compliance
	@$(MAKE) test
	@$(MAKE) compliance-report
	@echo "${GREEN}✅ Release Compliance Audit abgeschlossen${NC}"

# =============================================================================
# VENV-ENTWICKLUNGSUMGEBUNG-REGEL (NEUE REGEL)
# =============================================================================

## Virtual Environment Management
venv-setup: ## 🐍 Erstellt und konfiguriert venv für Development
	@echo "${BLUE}🐍 Erstelle und konfiguriere venv...${NC}"
	python scripts/venv_setup.py --setup
	@echo "${GREEN}✅ venv-Setup abgeschlossen${NC}"

venv-check: ## 🔍 Überprüft venv-Status und Gesundheit
	@echo "${BLUE}🔍 Überprüfe venv-Status...${NC}"
	python scripts/venv_check.py
	@echo "${GREEN}✅ venv-Check abgeschlossen${NC}"

venv-clean: ## 🗑️ Löscht venv komplett
	@echo "${BLUE}🗑️ Lösche venv...${NC}"
	python scripts/venv_setup.py --clean
	@echo "${GREEN}✅ venv gelöscht${NC}"

venv-clean-rebuild: ## 🔄 Löscht und erstellt venv neu
	@echo "${BLUE}🔄 Baue venv neu...${NC}"
	python scripts/venv_setup.py --clean
	python scripts/venv_setup.py --setup
	@echo "${GREEN}✅ venv neu erstellt${NC}"

venv-install-dev: ## 📦 Installiert Development-Dependencies
	@echo "${BLUE}📦 Installiere Development-Dependencies...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert! Führe '.venv\\Scripts\\activate' aus${NC}"; \
		exit 1; \
	fi
	pip install -r requirements/development.txt
	@echo "${GREEN}✅ Development-Dependencies installiert${NC}"

venv-install-test: ## 🧪 Installiert Test-Dependencies
	@echo "${BLUE}🧪 Installiere Test-Dependencies...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert! Führe '.venv\\Scripts\\activate' aus${NC}"; \
		exit 1; \
	fi
	pip install -r requirements/testing.txt
	@echo "${GREEN}✅ Test-Dependencies installiert${NC}"

venv-install-all: ## 📦 Installiert alle Dependencies
	@echo "${BLUE}📦 Installiere alle Dependencies...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert! Führe '.venv\\Scripts\\activate' aus${NC}"; \
		exit 1; \
	fi
	pip install -r requirements.txt
	pip install -r requirements/development.txt
	pip install -r requirements/testing.txt
	@echo "${GREEN}✅ Alle Dependencies installiert${NC}"

venv-sync: ## 🔄 Synchronisiert Dependencies
	@echo "${BLUE}🔄 Synchronisiere Dependencies...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert! Führe '.venv\\Scripts\\activate' aus${NC}"; \
		exit 1; \
	fi
	pip install --upgrade pip
	pip install --upgrade -r requirements/development.txt
	@echo "${GREEN}✅ Dependencies synchronisiert${NC}"

venv-validate: ## ✅ Validiert venv-Umgebung
	@echo "${BLUE}✅ Validiere venv-Umgebung...${NC}"
	python scripts/venv_check.py
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert!${NC}"; \
		exit 1; \
	else \
		echo "${GREEN}✅ venv ist aktiviert${NC}"; \
	fi
	@echo "${GREEN}✅ venv-Validierung abgeschlossen${NC}"

venv-requirements: ## 📋 Generiert requirements.txt aus aktueller venv
	@echo "${BLUE}📋 Generiere requirements.txt...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert! Führe '.venv\\Scripts\\activate' aus${NC}"; \
		exit 1; \
	fi
	pip freeze > requirements/current.txt
	@echo "${GREEN}✅ requirements/current.txt generiert${NC}"

venv-status: ## 📊 Zeigt venv-Status an
	@echo "${BLUE}📊 venv-Status:${NC}"
	@if [ -d ".venv" ]; then \
		echo "${GREEN}  venv existiert: ✅${NC}"; \
	else \
		echo "${RED}  venv existiert: ❌${NC}"; \
	fi
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "${GREEN}  venv aktiviert: ✅${NC}"; \
		echo "${BLUE}  venv Pfad: $$VIRTUAL_ENV${NC}"; \
		echo "${BLUE}  Python: $$(python --version)${NC}"; \
		echo "${BLUE}  pip: $$(pip --version)${NC}"; \
	else \
		echo "${RED}  venv aktiviert: ❌${NC}"; \
		echo "${YELLOW}  Aktivierung: .venv\\Scripts\\activate${NC}"; \
	fi

venv-info: ## ℹ️ Zeigt detaillierte venv-Informationen
	@echo "${BLUE}ℹ️ Detaillierte venv-Informationen:${NC}"
	@echo "${YELLOW}Projekt-Root: $$(pwd)${NC}"
	@echo "${YELLOW}System: $$(python -c "import platform; print(platform.system())")${NC}"
	@echo "${YELLOW}Python-Version: $$(python --version)${NC}"
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "${GREEN}venv aktiviert: $$VIRTUAL_ENV${NC}"; \
		echo "${BLUE}Installierte Pakete: $$(pip list | wc -l)${NC}"; \
		echo "${BLUE}pip-Version: $$(pip --version)${NC}"; \
	else \
		echo "${RED}venv nicht aktiviert${NC}"; \
	fi

venv-doctor: ## 🏥 Diagnose-Tool für venv-Probleme
	@echo "${BLUE}🏥 Führe venv-Diagnose durch...${NC}"
	python scripts/venv_check.py
	@echo "${YELLOW}Prüfe Platform-spezifische Konfiguration...${NC}"
	@if [ "$$(uname -s)" = "Windows_NT" ] || [ "$$(uname -o)" = "Msys" ]; then \
		echo "${BLUE}Windows-Umgebung erkannt${NC}"; \
		echo "${YELLOW}Aktivierung: .venv\\Scripts\\activate${NC}"; \
	else \
		echo "${BLUE}Unix-Umgebung erkannt${NC}"; \
		echo "${YELLOW}Aktivierung: source .venv/bin/activate${NC}"; \
	fi

venv-help: ## ❓ Zeigt venv-Hilfe an
	@echo "${GREEN}🐍 venv-Entwicklungsumgebung - Verfügbare Befehle:${NC}"
	@echo ""
	@echo "${YELLOW}Setup und Management:${NC}"
	@echo "  make venv-setup          - venv erstellen und konfigurieren"
	@echo "  make venv-clean          - venv löschen"
	@echo "  make venv-clean-rebuild  - venv neu erstellen"
	@echo "  make venv-check          - venv-Status überprüfen"
	@echo ""
	@echo "${YELLOW}Dependencies:${NC}"
	@echo "  make venv-install-dev    - Development-Dependencies"
	@echo "  make venv-install-test   - Test-Dependencies"
	@echo "  make venv-install-all    - Alle Dependencies"
	@echo "  make venv-sync           - Dependencies synchronisieren"
	@echo ""
	@echo "${YELLOW}Überwachung:${NC}"
	@echo "  make venv-status         - venv-Status anzeigen"
	@echo "  make venv-info           - Detaillierte Informationen"
	@echo "  make venv-validate       - venv-Umgebung validieren"
	@echo "  make venv-doctor         - Diagnose-Tool ausführen"
	@echo ""
	@echo "${YELLOW}Utilities:${NC}"
	@echo "  make venv-requirements   - requirements.txt generieren"
	@echo "  make venv-help           - Diese Hilfe anzeigen"
	@echo ""
	@echo "${YELLOW}Aktivierung:${NC}"
	@echo "  Windows:    .venv\\Scripts\\activate"
	@echo "  Linux/macOS: source .venv/bin/activate"

## venv-Guards für kritische Targets
venv-guard: ## 🛡️ Prüft ob venv aktiviert ist (interne Funktion)
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ FEHLER: venv nicht aktiviert!${NC}"; \
		echo "${YELLOW}Bitte führe aus: .venv\\Scripts\\activate${NC}"; \
		exit 1; \
	fi

## venv-Integration für bestehende Targets
install-with-venv: venv-guard install ## 📦 Installation mit venv-Check
install-dev-with-venv: venv-guard install-dev ## 🛠️ Development-Installation mit venv-Check
test-with-venv: venv-guard test ## 🧪 Tests mit venv-Check
format-with-venv: venv-guard format ## 🎨 Formatierung mit venv-Check
lint-with-venv: venv-guard lint ## 🔍 Linting mit venv-Check

## venv-Sicherheits-Checks
venv-security: ## 🔒 Security-Check der venv-Dependencies
	@echo "${BLUE}🔒 Führe Security-Check durch...${NC}"
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "${RED}❌ venv nicht aktiviert!${NC}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Prüfe auf Sicherheitslücken...${NC}"
	@pip-audit || echo "${YELLOW}⚠️ pip-audit nicht installiert${NC}"
	@safety check || echo "${YELLOW}⚠️ safety nicht installiert${NC}"
	@echo "${GREEN}✅ Security-Check abgeschlossen${NC}"

venv-audit: ## 📊 Umfassende venv-Audit
	@echo "${BLUE}📊 Führe umfassende venv-Audit durch...${NC}"
	@$(MAKE) venv-check
	@$(MAKE) venv-security
	@$(MAKE) venv-validate
	@echo "${GREEN}✅ venv-Audit abgeschlossen${NC}"

# =============================================================================
# UC-001 ENHANCED MANUAL ANALYSIS - SPEZIELLE TARGETS
# =============================================================================

## UC-001 Development und Testing
uc001-test: ## 🧪 UC-001 spezifische Tests ausführen
	@echo "${BLUE}🧪 Führe UC-001 Tests aus...${NC}"
	@if [ ! -d "tests/integration/uc001" ]; then \
		mkdir -p tests/integration/uc001; \
	fi
	pytest tests/integration/uc001/ -v --tb=short
	pytest tests/unit/ -k "uc001 or dossier or person" -v
	@echo "${GREEN}✅ UC-001 Tests abgeschlossen${NC}"

uc001-validate: ## ✅ UC-001 Schema und Performance-Validierung
	@echo "${BLUE}✅ Validiere UC-001 Implementierung...${NC}"
	@if [ -f "scripts/validate_uc001_schemas.py" ]; then \
		python scripts/validate_uc001_schemas.py; \
	else \
		echo "${YELLOW}⚠️ UC-001 Schema-Validator noch nicht implementiert${NC}"; \
	fi
	@if [ -f "scripts/check_uc001_performance.py" ]; then \
		python scripts/check_uc001_performance.py; \
	else \
		echo "${YELLOW}⚠️ UC-001 Performance-Check noch nicht implementiert${NC}"; \
	fi
	@echo "${GREEN}✅ UC-001 Validierung abgeschlossen${NC}"

uc001-deploy: ## 🚀 UC-001 Services deployen
	@echo "${BLUE}🚀 Deploye UC-001 Services...${NC}"
	@echo "${YELLOW}Starte UC-001 Core Services...${NC}"
	docker-compose up -d person_dossier video_context_analyzer clothing_analyzer
	@echo "${YELLOW}Warte auf Service-Start...${NC}"
	sleep 10
	@$(MAKE) dossier-check
	@echo "${GREEN}✅ UC-001 Services deployed${NC}"

dossier-check: ## 🔍 Dossier-System Health-Check
	@echo "${BLUE}🔍 Prüfe Dossier-System...${NC}"
	@echo "${YELLOW}Teste person_dossier Service...${NC}"
	@curl -s http://localhost:8005/health || echo "${RED}❌ person_dossier Service nicht erreichbar${NC}"
	@echo "${YELLOW}Teste Dossier-Verzeichnisse...${NC}"
	@if [ -d "data/dossiers" ]; then \
		echo "${GREEN}✅ data/dossiers existiert${NC}"; \
	else \
		mkdir -p data/dossiers; \
		echo "${YELLOW}⚠️ data/dossiers erstellt${NC}"; \
	fi
	@if [ -d "data/corrections" ]; then \
		echo "${GREEN}✅ data/corrections existiert${NC}"; \
	else \
		mkdir -p data/corrections; \
		echo "${YELLOW}⚠️ data/corrections erstellt${NC}"; \
	fi
	@echo "${GREEN}✅ Dossier-System Health-Check abgeschlossen${NC}"

uc001-status: ## 📊 UC-001 Status und Metriken anzeigen
	@echo "${BLUE}📊 UC-001 Status:${NC}"
	@echo "${YELLOW}Service-Status:${NC}"
	@docker-compose ps person_dossier video_context_analyzer clothing_analyzer || echo "${RED}Services nicht gestartet${NC}"
	@echo "${YELLOW}Dossier-Statistiken:${NC}"
	@if [ -d "data/dossiers" ]; then \
		echo "${BLUE}  Anzahl Dossiers: $$(find data/dossiers -name "*.json" | wc -l)${NC}"; \
	fi
	@if [ -d "data/corrections" ]; then \
		echo "${BLUE}  Anzahl Korrekturen: $$(find data/corrections -name "*.json" | wc -l)${NC}"; \
	fi
	@echo "${YELLOW}Performance-Metriken:${NC}"
	@if [ -f "data/uc001_metrics.json" ]; then \
		python -c "import json; data=json.load(open('data/uc001_metrics.json')); print(f'  Avg Dossier Update: {data.get(\"avg_dossier_update_time\", \"N/A\")}s'); print(f'  Re-ID Accuracy: {data.get(\"reid_accuracy\", \"N/A\")}%')" 2>/dev/null || echo "${YELLOW}  Keine Metriken verfügbar${NC}"; \
	else \
		echo "${YELLOW}  Keine Metriken verfügbar${NC}"; \
	fi

uc001-logs: ## 📋 UC-001 Service-Logs anzeigen
	@echo "${BLUE}📋 UC-001 Service-Logs:${NC}"
	@echo "${YELLOW}=== Person Dossier Service ===${NC}"
	docker-compose logs --tail=20 person_dossier || echo "${RED}person_dossier nicht verfügbar${NC}"
	@echo "${YELLOW}=== Video Context Analyzer ===${NC}"
	docker-compose logs --tail=20 video_context_analyzer || echo "${RED}video_context_analyzer nicht verfügbar${NC}"
	@echo "${YELLOW}=== Clothing Analyzer ===${NC}"
	docker-compose logs --tail=20 clothing_analyzer || echo "${RED}clothing_analyzer nicht verfügbar${NC}"

uc001-clean: ## 🗑️ UC-001 Daten bereinigen (VORSICHT!)
	@echo "${RED}⚠️ WARNUNG: Lösche alle UC-001 Daten!${NC}"
	@read -p "Bist du sicher? (ja/nein): " confirm && [ "$$confirm" = "ja" ] || exit 1
	@echo "${BLUE}🗑️ Lösche UC-001 Daten...${NC}"
	@rm -rf data/dossiers/* data/corrections/* data/uc001_metrics.json 2>/dev/null || true
	@echo "${GREEN}✅ UC-001 Daten gelöscht${NC}"

uc001-reset: ## 🔄 UC-001 Services zurücksetzen
	@echo "${BLUE}🔄 Setze UC-001 Services zurück...${NC}"
	docker-compose stop person_dossier video_context_analyzer clothing_analyzer
	docker-compose rm -f person_dossier video_context_analyzer clothing_analyzer
	@$(MAKE) uc001-deploy
	@echo "${GREEN}✅ UC-001 Services zurückgesetzt${NC}"

uc001-demo: ## 🎬 UC-001 Demo-Workflow ausführen
	@echo "${BLUE}🎬 Starte UC-001 Demo-Workflow...${NC}"
	@if [ ! -f "tests/demo/uc001_demo.py" ]; then \
		echo "${YELLOW}⚠️ UC-001 Demo-Script noch nicht implementiert${NC}"; \
		echo "${BLUE}Erstelle Demo-Struktur...${NC}"; \
		mkdir -p tests/demo; \
		echo "# UC-001 Demo-Script - TODO: Implementierung" > tests/demo/uc001_demo.py; \
	fi
	@echo "${GREEN}✅ UC-001 Demo vorbereitet${NC}"

uc001-docs: ## 📚 UC-001 Dokumentation aktualisieren
	@echo "${BLUE}📚 Aktualisiere UC-001 Dokumentation...${NC}"
	@if [ -f "docs/UC-001-ENHANCED-MANUAL-ANALYSIS.md" ]; then \
		echo "${GREEN}✅ UC-001 Hauptdokumentation vorhanden${NC}"; \
	else \
		echo "${RED}❌ UC-001 Hauptdokumentation fehlt${NC}"; \
	fi
	@echo "${YELLOW}Erstelle zusätzliche UC-001 Docs...${NC}"
	@mkdir -p docs/uc001
	@echo "# UC-001 API Reference" > docs/uc001/API.md
	@echo "# UC-001 Performance Metrics" > docs/uc001/METRICS.md
	@echo "# UC-001 Correction Workflow" > docs/uc001/CORRECTIONS.md
	@echo "${GREEN}✅ UC-001 Dokumentation aktualisiert${NC}"

uc001-help: ## ❓ UC-001 Hilfe anzeigen
	@echo "${GREEN}🎯 UC-001 Enhanced Manual Analysis - Verfügbare Befehle:${NC}"
	@echo ""
	@echo "${YELLOW}Development und Testing:${NC}"
	@echo "  make uc001-test        - UC-001 spezifische Tests"
	@echo "  make uc001-validate    - Schema und Performance-Validierung"
	@echo "  make uc001-demo        - Demo-Workflow ausführen"
	@echo ""
	@echo "${YELLOW}Deployment und Management:${NC}"
	@echo "  make uc001-deploy      - UC-001 Services deployen"
	@echo "  make uc001-reset       - Services zurücksetzen"
	@echo "  make dossier-check     - Dossier-System Health-Check"
	@echo ""
	@echo "${YELLOW}Monitoring und Logs:${NC}"
	@echo "  make uc001-status      - Status und Metriken anzeigen"
	@echo "  make uc001-logs        - Service-Logs anzeigen"
	@echo ""
	@echo "${YELLOW}Wartung:${NC}"
	@echo "  make uc001-clean       - Daten bereinigen (VORSICHT!)"
	@echo "  make uc001-docs        - Dokumentation aktualisieren"
	@echo "  make uc001-help        - Diese Hilfe anzeigen"
	@echo ""
	@echo "${YELLOW}Quality Gates (UC-001):${NC}"
	@echo "  - Dossier-Update: <10 Sekunden"
	@echo "  - Re-Identifikation: >90% Genauigkeit"
	@echo "  - Kleidungsklassifikation: >85% bei 200+ Kategorien"
	@echo "  - Video-Analyse: 1080p in <5 Minuten"

# Color definitions für venv-Targets
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# =============================================================================
# UC-001 ENHANCED MANUAL ANALYSIS - JOB MANAGER
# =============================================================================

uc001-start: ## Startet UC-001 Enhanced Manual Analysis Services
	@echo "🎯 Starting UC-001 Enhanced Manual Analysis services..."
	docker-compose up -d redis control person_dossier video_context_analyzer clothing_analyzer uc001_job_manager
	@echo "⏳ Waiting for UC-001 services to initialize..."
	sleep 60
	@$(MAKE) uc001-health

uc001-stop: ## Stoppt UC-001 Services
	@echo "🛑 Stopping UC-001 services..."
	docker-compose stop uc001_job_manager clothing_analyzer video_context_analyzer person_dossier

uc001-restart: uc001-stop uc001-start ## Startet UC-001 Services neu

uc001-health: ## Überprüft UC-001 Service-Health
	@echo "🏥 Checking UC-001 Enhanced Manual Analysis health..."
	@curl -f http://localhost:8012/health/uc001 > /dev/null 2>&1 && echo "✅ UC-001 Job Manager healthy" || echo "❌ UC-001 Job Manager not healthy"
	@curl -f http://localhost:8009/health > /dev/null 2>&1 && echo "✅ Person Dossier healthy" || echo "❌ Person Dossier not healthy"
	@curl -f http://localhost:8010/health > /dev/null 2>&1 && echo "✅ Video Context Analyzer healthy" || echo "❌ Video Context Analyzer not healthy"
	@curl -f http://localhost:8011/health > /dev/null 2>&1 && echo "✅ Clothing Analyzer healthy" || echo "❌ Clothing Analyzer not healthy"

uc001-status: ## Zeigt UC-001 Pipeline Status
	@echo "📊 UC-001 Enhanced Manual Analysis Pipeline Status:"
	@curl -s http://localhost:8012/uc001/pipeline/status | python -m json.tool 2>/dev/null || echo "❌ Unable to fetch pipeline status"

uc001-logs: ## Zeigt UC-001 Job Manager Logs
	@echo "📋 UC-001 Job Manager Logs (last 50 lines):"
	@docker logs --tail 50 ai_uc001_job_manager 2>/dev/null || echo "❌ UC-001 Job Manager container not found"

uc001-debug: ## Debug UC-001 Services
	@echo "🔍 UC-001 Enhanced Manual Analysis Debug Information:"
	@echo ""
	@echo "=== UC-001 SERVICE CONNECTIVITY ==="
	@curl -s http://localhost:8012/uc001/debug/services | python -m json.tool 2>/dev/null || echo "❌ Unable to fetch service debug info"
	@echo ""
	@echo "=== UC-001 JOB QUEUE ==="
	@curl -s http://localhost:8012/uc001/debug/queue | python -m json.tool 2>/dev/null || echo "❌ Unable to fetch queue debug info"

uc001-test: ## Testet UC-001 Pipeline mit Dummy-Job
	@echo "🧪 Testing UC-001 Enhanced Manual Analysis Pipeline..."
	@echo "Submitting test job..."
	@curl -X POST "http://localhost:8012/uc001/analyze/person" \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "media_path=/app/data/test/dummy.jpg&user_id=test_user" \
		2>/dev/null | python -m json.tool || echo "❌ UC-001 test failed"

uc001-metrics: ## Zeigt UC-001 Performance Metrics
	@echo "📈 UC-001 Pipeline Performance Metrics:"
	@curl -s http://localhost:8012/uc001/pipeline/metrics | python -m json.tool 2>/dev/null || echo "❌ Unable to fetch metrics"

# UC-001 Development Targets
uc001-build: ## Baut UC-001 Job Manager Docker Image
	@echo "🔨 Building UC-001 Job Manager..."
	docker-compose build uc001_job_manager

uc001-dev: ## Startet UC-001 im Development-Modus
	@echo "🛠️ Starting UC-001 in development mode..."
	@$(MAKE) uc001-build
	@$(MAKE) uc001-start
	@echo "🎯 UC-001 Development environment ready!"
	@echo "📖 API Documentation: http://localhost:8012/docs"
	@echo "🔧 Debug Endpoints: http://localhost:8012/uc001/debug/services"
