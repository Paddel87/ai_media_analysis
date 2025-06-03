#!/bin/bash
# Iteration Status Monitoring Script
# Version: 1.0.0

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service-Definitionen (aus Makefile übernommen)
ITERATION_1_SERVICES="job_manager control embedding_server llm_service"
ITERATION_2_SERVICES="vision_pipeline object_review person_dossier"
ITERATION_3_SERVICES="restraint_detection nsfw_detection thumbnail_generator guardrails"
ITERATION_4_SERVICES="llm_summarizer clip_service ui"

echo -e "${GREEN}📊 AI Media Analysis - Service-Integration Status${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Docker Compose Services zählen
ACTIVE_SERVICES=$(docker-compose config --services 2>/dev/null | wc -l)
echo -e "${YELLOW}Aktive Services in docker-compose.yml: ${ACTIVE_SERVICES}${NC}"
echo ""

# Iteration 1 Status
echo -e "${YELLOW}🔄 Iteration 1 - Management-Core (4 Services):${NC}"
for service in $ITERATION_1_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        if docker-compose ps $service 2>/dev/null | grep -q "Up"; then
            echo -e "  ✅ ${service} (running)"
        else
            echo -e "  🟡 ${service} (configured, not running)"
        fi
    else
        echo -e "  ⏳ ${service} (pending)"
    fi
done

# Iteration 2 Status
echo ""
echo -e "${YELLOW}🔄 Iteration 2 - AI-Processing-Core (3 Services):${NC}"
for service in $ITERATION_2_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        if docker-compose ps $service 2>/dev/null | grep -q "Up"; then
            echo -e "  ✅ ${service} (running)"
        else
            echo -e "  🟡 ${service} (configured, not running)"
        fi
    else
        echo -e "  ⏳ ${service} (pending)"
    fi
done

# Iteration 3 Status
echo ""
echo -e "${YELLOW}🔄 Iteration 3 - Specialized-Services (4 Services):${NC}"
for service in $ITERATION_3_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        if docker-compose ps $service 2>/dev/null | grep -q "Up"; then
            echo -e "  ✅ ${service} (running)"
        else
            echo -e "  🟡 ${service} (configured, not running)"
        fi
    else
        echo -e "  ⏳ ${service} (pending)"
    fi
done

# Iteration 4 Status
echo ""
echo -e "${YELLOW}🔄 Iteration 4 - Content & UI-Services (3 Services):${NC}"
for service in $ITERATION_4_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        if docker-compose ps $service 2>/dev/null | grep -q "Up"; then
            echo -e "  ✅ ${service} (running)"
        else
            echo -e "  🟡 ${service} (configured, not running)"
        fi
    else
        echo -e "  ⏳ ${service} (pending)"
    fi
done

# Gesamt-Status
echo ""
echo -e "${BLUE}===============================================${NC}"

# Zähle Services pro Iteration
ITERATION_1_COUNT=0
ITERATION_2_COUNT=0
ITERATION_3_COUNT=0
ITERATION_4_COUNT=0

for service in $ITERATION_1_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        ITERATION_1_COUNT=$((ITERATION_1_COUNT + 1))
    fi
done

for service in $ITERATION_2_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        ITERATION_2_COUNT=$((ITERATION_2_COUNT + 1))
    fi
done

for service in $ITERATION_3_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        ITERATION_3_COUNT=$((ITERATION_3_COUNT + 1))
    fi
done

for service in $ITERATION_4_SERVICES; do
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        ITERATION_4_COUNT=$((ITERATION_4_COUNT + 1))
    fi
done

TOTAL_NEW_SERVICES=$((ITERATION_1_COUNT + ITERATION_2_COUNT + ITERATION_3_COUNT + ITERATION_4_COUNT))

echo -e "${GREEN}📈 Integration-Fortschritt:${NC}"
echo -e "  Iteration 1: ${ITERATION_1_COUNT}/4 Services"
echo -e "  Iteration 2: ${ITERATION_2_COUNT}/3 Services"
echo -e "  Iteration 3: ${ITERATION_3_COUNT}/4 Services"
echo -e "  Iteration 4: ${ITERATION_4_COUNT}/3 Services"
echo -e "  ${GREEN}Gesamt neue Services: ${TOTAL_NEW_SERVICES}/14${NC}"
echo -e "  ${GREEN}Total Services: $((ACTIVE_SERVICES))/24${NC}"

# Memory Status (wenn Docker läuft)
echo ""
echo -e "${BLUE}💾 Resource-Status:${NC}"
if command -v docker &> /dev/null && docker ps >/dev/null 2>&1; then
    TOTAL_MEMORY=$(docker stats --no-stream --format "table {{.MemUsage}}" 2>/dev/null | grep -v "MEM" | awk -F'/' '{sum+=$1} END {print sum}' | sed 's/MiB//g' 2>/dev/null || echo "0")
    if [ ! -z "$TOTAL_MEMORY" ] && [ "$TOTAL_MEMORY" != "0" ]; then
        TOTAL_MEMORY_GB=$((TOTAL_MEMORY / 1024))
        echo -e "  Memory-Verbrauch: ~${TOTAL_MEMORY_GB}GB"

        if [ $TOTAL_MEMORY_GB -le 12 ]; then
            echo -e "  ${GREEN}✅ VPS-Ready (≤12GB)${NC}"
        elif [ $TOTAL_MEMORY_GB -le 16 ]; then
            echo -e "  ${YELLOW}🟡 Iteration 2 Limit (≤16GB)${NC}"
        elif [ $TOTAL_MEMORY_GB -le 20 ]; then
            echo -e "  ${YELLOW}🟡 Iteration 3 Limit (≤20GB)${NC}"
        else
            echo -e "  ${RED}⚠️ High Memory Usage (>20GB)${NC}"
        fi
    fi
else
    echo -e "  ${YELLOW}Docker nicht verfügbar${NC}"
fi

echo ""

# Nächste Schritte
if [ $ITERATION_1_COUNT -lt 4 ]; then
    echo -e "${BLUE}🎯 Nächster Schritt: make iteration-1${NC}"
elif [ $ITERATION_2_COUNT -lt 3 ]; then
    echo -e "${BLUE}🎯 Nächster Schritt: make iteration-2${NC}"
elif [ $ITERATION_3_COUNT -lt 4 ]; then
    echo -e "${BLUE}🎯 Nächster Schritt: make iteration-3${NC}"
elif [ $ITERATION_4_COUNT -lt 3 ]; then
    echo -e "${BLUE}🎯 Nächster Schritt: make iteration-4${NC}"
else
    echo -e "${GREEN}🎉 Alle 4 Iterationen abgeschlossen!${NC}"
    echo -e "${GREEN}🚀 Bereit für Alpha 0.6.0${NC}"
fi

echo ""
