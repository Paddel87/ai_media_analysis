#!/bin/bash
# Comprehensive Health Check Script für alle Services
# Version: 1.0.0

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
TIMEOUT=10
RETRIES=3
VERBOSE=${1:-false}

echo -e "${GREEN}🏥 AI Media Analysis - Comprehensive Health Check${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Service-Port-Mapping
declare -A SERVICE_PORTS
SERVICE_PORTS[nginx]="80"
SERVICE_PORTS[redis]="6379"
SERVICE_PORTS[vector-db]="8002"
SERVICE_PORTS[data-persistence]="8003"
SERVICE_PORTS[pose_estimation]="8004"
SERVICE_PORTS[ocr_detection]="8005"
SERVICE_PORTS[clip_nsfw]="8006"
SERVICE_PORTS[face_reid]="8007"
SERVICE_PORTS[whisper_transcriber]="8001"
SERVICE_PORTS[streamlit-ui]="8501"

# Neue Services (iterative Integration)
SERVICE_PORTS[job_manager]="8010"
SERVICE_PORTS[control]="8011"
SERVICE_PORTS[embedding_server]="8012"
SERVICE_PORTS[llm_service]="8013"
SERVICE_PORTS[vision_pipeline]="8014"
SERVICE_PORTS[object_review]="8015"
SERVICE_PORTS[person_dossier]="8016"
SERVICE_PORTS[restraint_detection]="8017"
SERVICE_PORTS[nsfw_detection]="8018"
SERVICE_PORTS[thumbnail_generator]="8019"
SERVICE_PORTS[guardrails]="8020"
SERVICE_PORTS[llm_summarizer]="8021"
SERVICE_PORTS[clip_service]="8022"
SERVICE_PORTS[ui]="8080"

# Health-Check-Funktion
check_service_health() {
    local service=$1
    local port=${SERVICE_PORTS[$service]}
    local endpoint="health"

    if [ -z "$port" ]; then
        echo -e "  ${RED}❌ ${service}: Unbekannter Service${NC}"
        return 1
    fi

    # Container-Status prüfen
    if ! docker-compose ps $service 2>/dev/null | grep -q "Up"; then
        echo -e "  ${RED}❌ ${service}: Container nicht running${NC}"
        return 1
    fi

    # Spezielle Health-Checks für verschiedene Services
    case $service in
        "redis")
            if docker exec ai_media_analysis_redis_1 redis-cli ping >/dev/null 2>&1; then
                echo -e "  ${GREEN}✅ ${service}: Redis PING successful${NC}"
                return 0
            else
                echo -e "  ${RED}❌ ${service}: Redis PING failed${NC}"
                return 1
            fi
            ;;
        "nginx")
            if curl -f -s --max-time $TIMEOUT http://localhost/health >/dev/null 2>&1; then
                echo -e "  ${GREEN}✅ ${service}: HTTP health check successful${NC}"
                return 0
            else
                echo -e "  ${RED}❌ ${service}: HTTP health check failed${NC}"
                return 1
            fi
            ;;
        *)
            # Standard HTTP Health-Check
            local url="http://localhost:${port}/${endpoint}"
            if curl -f -s --max-time $TIMEOUT $url >/dev/null 2>&1; then
                echo -e "  ${GREEN}✅ ${service}: Health check successful (${port})${NC}"
                if [ "$VERBOSE" = "true" ]; then
                    local response=$(curl -s --max-time $TIMEOUT $url 2>/dev/null)
                    echo -e "    Response: $response"
                fi
                return 0
            else
                echo -e "  ${RED}❌ ${service}: Health check failed (${port})${NC}"
                if [ "$VERBOSE" = "true" ]; then
                    echo -e "    URL: $url"
                    echo -e "    Timeout: ${TIMEOUT}s"
                fi
                return 1
            fi
            ;;
    esac
}

# Alle konfigurierten Services finden
CONFIGURED_SERVICES=$(docker-compose config --services 2>/dev/null)

if [ -z "$CONFIGURED_SERVICES" ]; then
    echo -e "${RED}❌ Keine Services in docker-compose.yml gefunden${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Prüfe $(echo "$CONFIGURED_SERVICES" | wc -w) konfigurierte Services...${NC}"
echo ""

# Infrastructure Services
echo -e "${BLUE}🏗️ Infrastructure Services:${NC}"
INFRA_SERVICES="nginx redis vector-db data-persistence"
INFRA_HEALTHY=0
INFRA_TOTAL=0

for service in $INFRA_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        INFRA_TOTAL=$((INFRA_TOTAL + 1))
        if check_service_health $service; then
            INFRA_HEALTHY=$((INFRA_HEALTHY + 1))
        fi
    fi
done

# AI Processing Services
echo ""
echo -e "${BLUE}🤖 AI Processing Services:${NC}"
AI_SERVICES="pose_estimation ocr_detection clip_nsfw face_reid whisper_transcriber"
AI_HEALTHY=0
AI_TOTAL=0

for service in $AI_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        AI_TOTAL=$((AI_TOTAL + 1))
        if check_service_health $service; then
            AI_HEALTHY=$((AI_HEALTHY + 1))
        fi
    fi
done

# Management Services (Iteration 1)
echo ""
echo -e "${BLUE}📋 Management Services (Iteration 1):${NC}"
MGMT_SERVICES="job_manager control embedding_server llm_service"
MGMT_HEALTHY=0
MGMT_TOTAL=0

for service in $MGMT_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        MGMT_TOTAL=$((MGMT_TOTAL + 1))
        if check_service_health $service; then
            MGMT_HEALTHY=$((MGMT_HEALTHY + 1))
        fi
    fi
done

# Processing Services (Iteration 2)
echo ""
echo -e "${BLUE}⚙️ Processing Services (Iteration 2):${NC}"
PROC_SERVICES="vision_pipeline object_review person_dossier"
PROC_HEALTHY=0
PROC_TOTAL=0

for service in $PROC_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        PROC_TOTAL=$((PROC_TOTAL + 1))
        if check_service_health $service; then
            PROC_HEALTHY=$((PROC_HEALTHY + 1))
        fi
    fi
done

# Specialized Services (Iteration 3)
echo ""
echo -e "${BLUE}🎯 Specialized Services (Iteration 3):${NC}"
SPEC_SERVICES="restraint_detection nsfw_detection thumbnail_generator guardrails"
SPEC_HEALTHY=0
SPEC_TOTAL=0

for service in $SPEC_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        SPEC_TOTAL=$((SPEC_TOTAL + 1))
        if check_service_health $service; then
            SPEC_HEALTHY=$((SPEC_HEALTHY + 1))
        fi
    fi
done

# UI Services (Iteration 4)
echo ""
echo -e "${BLUE}🖥️ UI Services (Iteration 4):${NC}"
UI_SERVICES="streamlit-ui llm_summarizer clip_service ui"
UI_HEALTHY=0
UI_TOTAL=0

for service in $UI_SERVICES; do
    if echo "$CONFIGURED_SERVICES" | grep -q "^${service}$"; then
        UI_TOTAL=$((UI_TOTAL + 1))
        if check_service_health $service; then
            UI_HEALTHY=$((UI_HEALTHY + 1))
        fi
    fi
done

# Gesamt-Zusammenfassung
echo ""
echo -e "${BLUE}===================================================${NC}"
echo -e "${GREEN}📊 Health Check Zusammenfassung:${NC}"

TOTAL_HEALTHY=$((INFRA_HEALTHY + AI_HEALTHY + MGMT_HEALTHY + PROC_HEALTHY + SPEC_HEALTHY + UI_HEALTHY))
TOTAL_SERVICES=$((INFRA_TOTAL + AI_TOTAL + MGMT_TOTAL + PROC_TOTAL + SPEC_TOTAL + UI_TOTAL))

echo -e "  Infrastructure: ${INFRA_HEALTHY}/${INFRA_TOTAL} healthy"
echo -e "  AI Processing: ${AI_HEALTHY}/${AI_TOTAL} healthy"
echo -e "  Management: ${MGMT_HEALTHY}/${MGMT_TOTAL} healthy"
echo -e "  Processing: ${PROC_HEALTHY}/${PROC_TOTAL} healthy"
echo -e "  Specialized: ${SPEC_HEALTHY}/${SPEC_TOTAL} healthy"
echo -e "  UI Services: ${UI_HEALTHY}/${UI_TOTAL} healthy"

echo ""
if [ $TOTAL_HEALTHY -eq $TOTAL_SERVICES ] && [ $TOTAL_SERVICES -gt 0 ]; then
    echo -e "${GREEN}🎉 Alle ${TOTAL_SERVICES} Services sind healthy!${NC}"
    SUCCESS_RATE=100
elif [ $TOTAL_SERVICES -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Keine Services konfiguriert${NC}"
    SUCCESS_RATE=0
else
    SUCCESS_RATE=$((TOTAL_HEALTHY * 100 / TOTAL_SERVICES))
    echo -e "${YELLOW}⚠️ ${TOTAL_HEALTHY}/${TOTAL_SERVICES} Services healthy (${SUCCESS_RATE}%)${NC}"
fi

# Performance-Metrics
echo ""
echo -e "${BLUE}💾 Performance-Metrics:${NC}"
if command -v docker &> /dev/null && docker ps >/dev/null 2>&1; then
    echo -e "  CPU Usage:"
    docker stats --no-stream --format "    {{.Name}}: {{.CPUPerc}}" | head -5
    echo ""
    echo -e "  Memory Usage:"
    docker stats --no-stream --format "    {{.Name}}: {{.MemUsage}}" | head -5
else
    echo -e "  ${YELLOW}Docker stats nicht verfügbar${NC}"
fi

# Empfehlungen
echo ""
echo -e "${BLUE}💡 Empfehlungen:${NC}"
if [ $SUCCESS_RATE -lt 100 ] && [ $TOTAL_SERVICES -gt 0 ]; then
    echo -e "  • Prüfe Docker-Logs für fehlgeschlagene Services: docker-compose logs <service>"
    echo -e "  • Starte Services neu: docker-compose restart <service>"
    echo -e "  • Führe vollständigen Restart durch: make restart-services"
fi

if [ $MGMT_TOTAL -eq 0 ]; then
    echo -e "  • Starte Service-Integration: make iteration-1"
fi

# Exit-Code basierend auf Success-Rate
if [ $SUCCESS_RATE -eq 100 ] && [ $TOTAL_SERVICES -gt 0 ]; then
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    exit 1
else
    exit 2
fi
