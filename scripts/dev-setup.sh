#!/bin/bash
set -e

# AI Media Analysis System - Development Setup Script
# Automatisiert die komplette Entwicklungsumgebung-Einrichtung

# Farben für bessere Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# System-Check-Funktionen
check_system() {
    log_info "Checking system requirements..."
    
    # Python Version Check
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 0 ]]; then
        log_error "Python 3.9+ required, found $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python $PYTHON_VERSION found"
    
    # Docker Check
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    log_success "Docker found"
    
    # Docker Compose Check
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi
    log_success "Docker Compose found"
    
    # Git Check
    if ! command -v git &> /dev/null; then
        log_error "Git is required but not installed"
        exit 1
    fi
    log_success "Git found"
    
    # Make Check
    if ! command -v make &> /dev/null; then
        log_warning "Make not found, using python scripts instead"
    else
        log_success "Make found"
    fi
}

# Virtual Environment Setup
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Aktiviere Virtual Environment
    source venv/bin/activate || source venv/Scripts/activate
    log_success "Virtual environment activated"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    log_success "pip upgraded"
}

# Dependencies Installation
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Development Dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Main dependencies installed"
    fi
    
    # CI Dependencies
    if [ -f "requirements-ci.txt" ]; then
        pip install -r requirements-ci.txt
        log_success "CI dependencies installed"
    fi
    
    # Development Tools
    pip install pre-commit black isort flake8 mypy bandit safety
    log_success "Development tools installed"
}

# Environment Configuration
setup_environment() {
    log_info "Setting up environment configuration..."
    
    # Create config directory
    mkdir -p config logs data/{uploads,results,backups}
    log_success "Directory structure created"
    
    # Copy environment template
    if [ -f "config/environment.example" ] && [ ! -f ".env" ]; then
        cp config/environment.example .env
        log_success "Environment file created from template"
        log_warning "Please edit .env file with your specific configuration"
    fi
    
    # Redis Configuration
    if [ ! -f "config/redis.conf" ]; then
        cat > config/redis.conf << EOF
# Redis VPS-optimierte Konfiguration
bind 0.0.0.0
port 6379
timeout 300
keepalive 60
databases 16
save 900 1
save 300 10
save 60 10000
maxmemory 1gb
maxmemory-policy allkeys-lru
EOF
        log_success "Redis configuration created"
    fi
}

# Pre-commit Hooks Setup
setup_precommit() {
    log_info "Setting up pre-commit hooks..."
    
    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "No pre-commit config found, creating basic setup..."
        cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF
        pre-commit install
        log_success "Basic pre-commit setup created and installed"
    fi
}

# Docker Setup
setup_docker() {
    log_info "Setting up Docker environment..."
    
    # Build Docker images (development versions)
    log_info "Building Docker images for development..."
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        # Build only core services for development
        docker-compose build redis vector-db data-persistence nginx
        log_success "Core Docker services built"
    else
        log_error "docker-compose.yml not found"
        exit 1
    fi
}

# Test Environment Setup
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Run environment check
    python run_tests.py --check-env
    
    # Run a quick test to verify setup
    log_info "Running quick test suite..."
    python run_tests.py --unit -v | head -20
    
    log_success "Test environment verified"
}

# Nginx Configuration
setup_nginx() {
    log_info "Setting up Nginx configuration..."
    
    mkdir -p config/nginx
    
    if [ ! -f "config/nginx/default.conf" ]; then
        cat > config/nginx/default.conf << EOF
# AI Media Analysis - Development Nginx Configuration
upstream vector_db {
    server vector-db:8000;
}

upstream whisper_service {
    server whisper_transcriber:8000;
}

upstream streamlit_ui {
    server streamlit-ui:8501;
}

server {
    listen 80;
    server_name localhost;
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Vector DB API
    location /api/vector/ {
        proxy_pass http://vector_db/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Whisper API
    location /api/whisper/ {
        proxy_pass http://whisper_service/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Streamlit UI
    location / {
        proxy_pass http://streamlit_ui;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
        log_success "Nginx configuration created"
    fi
}

# Development Helpers
create_development_helpers() {
    log_info "Creating development helper scripts..."
    
    # Quick start script
    cat > scripts/quick-start.sh << 'EOF'
#!/bin/bash
# Quick start for development
echo "🚀 Starting AI Media Analysis Development Environment..."

# Start core services
docker-compose up -d redis vector-db data-persistence

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Check service health
make health-check

echo "✅ Development environment ready!"
echo "📊 Access Streamlit UI: http://localhost:8501"
echo "🔍 Vector DB API: http://localhost:8002"
echo "🎤 Whisper API: http://localhost:8001"
EOF
    chmod +x scripts/quick-start.sh
    
    # Stop script
    cat > scripts/stop-all.sh << 'EOF'
#!/bin/bash
# Stop all services
echo "🛑 Stopping all services..."
docker-compose down
echo "✅ All services stopped"
EOF
    chmod +x scripts/stop-all.sh
    
    # Reset script
    cat > scripts/reset-dev.sh << 'EOF'
#!/bin/bash
# Reset development environment
echo "🔄 Resetting development environment..."
docker-compose down -v
docker system prune -f
rm -rf data/uploads/* data/results/* logs/*
echo "✅ Development environment reset"
EOF
    chmod +x scripts/reset-dev.sh
    
    log_success "Development helper scripts created"
}

# Main setup function
main() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   AI Media Analysis - Development Setup"
    echo "=================================================="
    echo -e "${NC}"
    
    # Parse command line arguments
    SKIP_DOCKER=false
    QUICK_SETUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --quick)
                QUICK_SETUP=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--skip-docker] [--quick] [--help]"
                echo "  --skip-docker  Skip Docker setup"
                echo "  --quick        Quick setup (minimal)"
                echo "  --help         Show this help"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_system
    setup_venv
    install_dependencies
    setup_environment
    
    if [ "$QUICK_SETUP" = false ]; then
        setup_precommit
        setup_nginx
        create_development_helpers
        
        if [ "$SKIP_DOCKER" = false ]; then
            setup_docker
        fi
        
        setup_test_environment
    fi
    
    echo
    echo -e "${GREEN}"
    echo "=================================================="
    echo "   🎉 Development Setup Complete!"
    echo "=================================================="
    echo -e "${NC}"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run 'scripts/quick-start.sh' to start services"
    echo "3. Run 'make test' to verify everything works"
    echo "4. Start coding! 🚀"
    echo
    echo "Useful commands:"
    echo "  make help           - Show all available commands"
    echo "  make test           - Run test suite"
    echo "  make run-services   - Start all Docker services"
    echo "  make logs           - Show service logs"
    echo
}

# Run main function
main "$@" 