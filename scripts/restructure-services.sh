#!/bin/bash
# AI Media Analysis - Service-Strukturierung Script
# Erstellt einheitliche services/ Struktur und entfernt Root-Level-Duplikate

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Backup erstellen
create_backup() {
    log_info "Creating backup before restructuring..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup der Root-Level-Services
    for dir in control embedding_server llm_interface object_review ocr_logo_title preprocess qdrant streamlit_ui vector_db whisper vision_pipeline; do
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BACKUP_DIR/"
            log_success "Backed up $dir"
        fi
    done
    
    log_success "Backup created in $BACKUP_DIR"
}

# Kategorisierte services/ Struktur erstellen
create_categorized_structure() {
    log_info "Creating categorized services structure..."
    
    # Infrastructure Services (VPS-Services)
    mkdir -p services/infrastructure
    log_info "Created services/infrastructure/"
    
    # AI Processing Services (Cloud AI-Services)  
    mkdir -p services/ai_processing
    log_info "Created services/ai_processing/"
    
    # Management Services (Job & Cloud Management)
    mkdir -p services/management
    log_info "Created services/management/"
    
    # UI Services
    mkdir -p services/ui_interfaces
    log_info "Created services/ui_interfaces/"
    
    log_success "Categorized structure created"
}

# Services kategorisieren (nur Planung, nicht verschieben)
plan_service_categorization() {
    log_info "Planning service categorization..."
    
    echo ""
    echo "🏗️  INFRASTRUCTURE SERVICES (VPS):"
    echo "   nginx/ → services/infrastructure/nginx/"
    echo "   vector_db/ → services/infrastructure/vector_db/"
    echo "   (redis config wird über config/ verwaltet)"
    
    echo ""
    echo "🤖 AI PROCESSING SERVICES (Cloud AI):"
    echo "   pose_estimation/ → services/ai_processing/pose_estimation/"
    echo "   ocr_detection/ → services/ai_processing/ocr_detection/"
    echo "   clip_nsfw/ → services/ai_processing/clip_nsfw/"
    echo "   face_reid/ → services/ai_processing/face_reid/"
    echo "   whisper_transcriber/ → services/ai_processing/whisper_transcriber/"
    
    echo ""
    echo "⚙️  MANAGEMENT SERVICES:"
    echo "   job_manager/ → services/management/job_manager/"
    echo "   (cloud_manager/ → neu für Vast.ai Integration)"
    
    echo ""
    echo "🖥️  UI SERVICES:"
    echo "   ui/ → services/ui_interfaces/streamlit_ui/"
    echo "   (api_gateway/ → neu für REST API)"
    
    echo ""
    echo "🗑️  ROOT-LEVEL DUPLIKATE (zur Löschung vorgesehen):"
    echo "   control/ (→ services/control/ bereits vorhanden)"
    echo "   embedding_server/ (→ services/embedding_server/ bereits vorhanden)"
    echo "   llm_interface/ (→ services/llm_service/ bereits vorhanden)"
    echo "   object_review/ (→ services/object_review/ bereits vorhanden)"
    echo "   ocr_logo_title/ (→ services/ocr_detection/ bereits vorhanden)"
    echo "   preprocess/ (→ kann in services/common/ integriert werden)"
    echo "   qdrant/ (→ ersetzt durch services/vector_db/)"
    echo "   streamlit_ui/ (→ services/ui/ bereits vorhanden)"
    echo "   vector_db/ (→ services/vector_db/ bereits vorhanden)"
    echo "   whisper/ (→ services/whisper_transcriber/ bereits vorhanden)"
    echo "   vision_pipeline/ (→ services/vision_pipeline/ bereits vorhanden)"
}

# Root-Level-Duplikate sicher entfernen (mit Bestätigung)
remove_root_level_duplicates() {
    log_warning "WICHTIG: Root-Level-Duplikate werden gelöscht!"
    log_warning "Backup wurde erstellt. Fortfahren? (y/N)"
    
    # In automatisierten Umgebungen nicht ausführen
    if [ "$1" != "--auto" ]; then
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Abgebrochen. Backup bleibt erhalten."
            return 0
        fi
    fi
    
    log_info "Removing root-level duplicates..."
    
    ROOT_DUPLICATES=(
        "control"
        "embedding_server" 
        "llm_interface"
        "object_review"
        "ocr_logo_title"
        "preprocess"
        "qdrant"
        "streamlit_ui"
        "vector_db"
        "whisper"
        "vision_pipeline"
    )
    
    for dir in "${ROOT_DUPLICATES[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            log_success "Removed redundant $dir/"
        else
            log_info "$dir/ does not exist (already clean)"
        fi
    done
    
    log_success "Root-level duplicates removed"
}

# Docker-Compose-Referenzen prüfen
check_docker_compose_references() {
    log_info "Checking docker-compose.yml references..."
    
    if grep -q "context: \./" docker-compose.yml; then
        log_warning "Found root-level context references in docker-compose.yml"
        log_info "These will need to be updated to services/ paths"
    fi
    
    if grep -q "services/" docker-compose.yml; then
        log_success "Found services/ references in docker-compose.yml"
    fi
    
    log_info "Manual review of docker-compose.yml recommended after restructuring"
}

# Haupt-Ausführung
main() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   AI Media Analysis - Service Restructuring"
    echo "=================================================="
    echo -e "${NC}"
    
    # Nur planen, nicht automatisch ausführen
    if [ "$1" == "--plan-only" ]; then
        plan_service_categorization
        check_docker_compose_references
        return 0
    fi
    
    # Vollständige Ausführung
    create_backup
    plan_service_categorization
    
    log_warning "Möchten Sie die kategorisierte Struktur erstellen? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        create_categorized_structure
    fi
    
    log_warning "Möchten Sie Root-Level-Duplikate entfernen? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        remove_root_level_duplicates
    fi
    
    check_docker_compose_references
    
    echo ""
    log_success "Service restructuring completed!"
    echo ""
    echo "Nächste Schritte:"
    echo "1. Services manuell in kategorisierte Verzeichnisse verschieben"
    echo "2. docker-compose.yml Pfade aktualisieren"
    echo "3. Makefile-Commands anpassen"
    echo "4. Tests ausführen: make test"
}

# Script ausführen
main "$@" 