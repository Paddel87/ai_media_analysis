#!/usr/bin/env python3
"""
Script zur automatischen Generierung von docker-compose.yml Service-Konfigurationen
für die iterative Service-Integration in Alpha 0.5.0
"""

import sys
import yaml
import os
from typing import Dict, Any

# Service-Port-Mapping (um Port-Konflikte zu vermeiden)
SERVICE_PORTS = {
    'job_manager': 8010,
    'control': 8011,
    'embedding_server': 8012,
    'llm_service': 8013,
    'vision_pipeline': 8014,
    'object_review': 8015,
    'person_dossier': 8016,
    'restraint_detection': 8017,
    'nsfw_detection': 8018,
    'thumbnail_generator': 8019,
    'guardrails': 8020,
    'llm_summarizer': 8021,
    'clip_service': 8022,
    'ui': 8080,  # Production UI auf Standard-HTTP-Port
}

# Service-Kategorien mit spezifischen Konfigurationen
SERVICE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # Management Services
    'job_manager': {
        'description': 'Task-Orchestrierung und Batch-Management',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/jobs:/app/data/jobs',
            './logs/job_manager:/app/logs'
        ],
        'environment': [
            'BATCH_THRESHOLD_HOURS=4',
            'MIN_JOBS_PER_BATCH=3',
            'AUTO_PROCESS_JOBS=true',
            'VAST_API_KEY=${VAST_API_KEY}',
        ],
        'depends_on': ['redis']
    },
    'control': {
        'description': 'System-Control und Service-Management',
        'memory_limit': '1G',
        'cpu_limit': '1',
        'replicas': 1,
        'volumes': [
            './logs/control:/app/logs',
            './config/control:/app/config:ro'
        ],
        'environment': [
            'SYSTEM_MODE=production',
            'MONITORING_ENABLED=true'
        ],
        'depends_on': ['redis']
    },
    'embedding_server': {
        'description': 'Vector-Embedding-Management',
        'memory_limit': '3G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/embeddings:/app/embeddings',
            './logs/embedding_server:/app/logs'
        ],
        'environment': [
            'EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2',
            'VECTOR_DB_HOST=vector-db',
            'VECTOR_DB_PORT=8000'
        ],
        'depends_on': ['redis', 'vector-db']
    },
    'llm_service': {
        'description': 'Language-Model-Interface',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './logs/llm_service:/app/logs',
            './config/llm:/app/config:ro'
        ],
        'environment': [
            'OPENAI_API_KEY=${OPENAI_API_KEY}',
            'ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}',
            'FALLBACK_MODEL=local',
            'COST_TRACKING_ENABLED=true'
        ],
        'depends_on': ['redis']
    },

    # AI Processing Services
    'vision_pipeline': {
        'description': 'Video-Processing-Pipeline',
        'memory_limit': '4G',
        'cpu_limit': '4',
        'replicas': 1,
        'volumes': [
            './data/videos:/app/videos',
            './data/results:/app/results',
            './logs/vision_pipeline:/app/logs'
        ],
        'environment': [
            'PROCESSING_MODE=cpu',
            'CLOUD_AI_ENABLED=true',
            'BATCH_SIZE=1',
            'MAX_VIDEO_SIZE=1GB'
        ],
        'depends_on': ['redis', 'job_manager']
    },
    'object_review': {
        'description': 'Object-Detection-Review-System',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/reviews:/app/reviews',
            './logs/object_review:/app/logs'
        ],
        'environment': [
            'REVIEW_MODE=manual',
            'AUTO_APPROVE_THRESHOLD=0.95',
            'HUMAN_REVIEW_REQUIRED=true'
        ],
        'depends_on': ['redis']
    },
    'person_dossier': {
        'description': 'Person-Tracking-System',
        'memory_limit': '3G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/dossiers:/app/dossiers',
            './data/faces:/app/faces',
            './logs/person_dossier:/app/logs'
        ],
        'environment': [
            'FACE_REID_HOST=face_reid',
            'FACE_REID_PORT=8000',
            'SIMILARITY_THRESHOLD=0.8',
            'PRIVACY_MODE=enabled'
        ],
        'depends_on': ['redis', 'face_reid']
    },

    # Specialized Services
    'restraint_detection': {
        'description': 'Specialized BDSM/Restraint-Detection',
        'memory_limit': '3G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/results:/app/results',
            './logs/restraint_detection:/app/logs',
            './models/restraint:/app/models:ro'
        ],
        'environment': [
            'MODEL_TYPE=custom',
            'CONFIDENCE_THRESHOLD=0.7',
            'UC001_ENHANCED_MODE=true'
        ],
        'depends_on': ['redis']
    },
    'nsfw_detection': {
        'description': 'Enhanced NSFW-Detection',
        'memory_limit': '3G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/results:/app/results',
            './logs/nsfw_detection:/app/logs'
        ],
        'environment': [
            'ENSEMBLE_MODE=true',
            'SEVERITY_LEVELS=true',
            'FALSE_POSITIVE_REDUCTION=enabled'
        ],
        'depends_on': ['redis', 'clip_nsfw']
    },
    'thumbnail_generator': {
        'description': 'Video-Thumbnail-Generation',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/videos:/app/videos:ro',
            './data/thumbnails:/app/thumbnails',
            './logs/thumbnail_generator:/app/logs'
        ],
        'environment': [
            'SMART_SELECTION=true',
            'COMPRESSION_ENABLED=true',
            'THUMBNAIL_SIZE=320x240'
        ],
        'depends_on': ['redis']
    },
    'guardrails': {
        'description': 'Content-Safety-Filtering',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './config/policies:/app/policies:ro',
            './logs/guardrails:/app/logs'
        ],
        'environment': [
            'POLICY_ENGINE=enabled',
            'REAL_TIME_BLOCKING=true',
            'AUDIT_LOGGING=enabled'
        ],
        'depends_on': ['redis']
    },

    # Content & UI Services
    'llm_summarizer': {
        'description': 'AI-Content-Summarization',
        'memory_limit': '2G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './logs/llm_summarizer:/app/logs'
        ],
        'environment': [
            'MULTI_LANGUAGE=true',
            'CONTEXT_AWARE=true',
            'COST_OPTIMIZATION=enabled'
        ],
        'depends_on': ['redis', 'llm_service']
    },
    'clip_service': {
        'description': 'Enhanced CLIP-Integration',
        'memory_limit': '4G',
        'cpu_limit': '2',
        'replicas': 1,
        'volumes': [
            './data/embeddings:/app/embeddings',
            './logs/clip_service:/app/logs'
        ],
        'environment': [
            'CUSTOM_EMBEDDINGS=true',
            'SIMILARITY_SEARCH=enabled',
            'PERFORMANCE_MODE=optimized'
        ],
        'depends_on': ['redis', 'embedding_server']
    },
    'ui': {
        'description': 'Production Web-Interface',
        'memory_limit': '1G',
        'cpu_limit': '1',
        'replicas': 1,
        'volumes': [
            './logs/ui:/app/logs'
        ],
        'environment': [
            'PRODUCTION_MODE=true',
            'MULTI_USER_SUPPORT=true',
            'RBAC_ENABLED=true',
            'API_BASE_URL=http://nginx'
        ],
        'depends_on': ['nginx', 'redis']
    }
}

def generate_service_config(service_name: str) -> Dict[str, Any]:
    """Generiert docker-compose.yml Konfiguration für einen Service"""

    if service_name not in SERVICE_CONFIGS:
        raise ValueError(f"Service '{service_name}' nicht in SERVICE_CONFIGS definiert")

    config = SERVICE_CONFIGS[service_name]
    port = SERVICE_PORTS.get(service_name, 8000)

    # Type-safe Zugriffe
    memory_limit = str(config['memory_limit'])
    cpu_limit = str(config['cpu_limit'])
    volumes = config['volumes']
    environment = config['environment']
    depends_on = config['depends_on']

    # Memory-Berechnung für reservations
    memory_gb = int(memory_limit.rstrip('G'))
    reserved_memory = str(memory_gb // 2) + 'G'
    reserved_cpu = str(float(cpu_limit) / 2)

    service_config = {
        'build': {
            'context': f'./services/{service_name}',
            'dockerfile': 'Dockerfile.cpu'
        },
        'container_name': f'ai_{service_name}',
        'ports': [f'{port}:8000'],
        'volumes': volumes,
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOG_LEVEL=INFO',
            'REDIS_HOST=redis',
            'REDIS_PORT=6379',
            'CLOUD_MODE=false'  # VPS-Modus
        ] + environment,
        'depends_on': {
            dep: {'condition': 'service_healthy'} for dep in depends_on
        },
        'networks': ['ai_network'],
        'deploy': {
            'resources': {
                'limits': {
                    'cpus': cpu_limit,
                    'memory': memory_limit
                },
                'reservations': {
                    'cpus': reserved_cpu,
                    'memory': reserved_memory
                }
            }
        },
        'healthcheck': {
            'test': ['CMD', 'curl', '-f', 'http://localhost:8000/health'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3,
            'start_period': '60s'
        },
        'restart': 'unless-stopped',
        'logging': {
            'driver': 'json-file',
            'options': {
                'max-size': '10m',
                'max-file': '3'
            }
        }
    }

    return service_config

def update_docker_compose(service_name: str) -> bool:
    """Fügt Service zu docker-compose.yml hinzu"""

    compose_file = 'docker-compose.yml'

    if not os.path.exists(compose_file):
        print(f"❌ {compose_file} nicht gefunden")
        return False

    try:
        # Aktuelle docker-compose.yml laden
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)

        # Service-Konfiguration generieren
        service_config = generate_service_config(service_name)

        # Service hinzufügen
        if 'services' not in compose_data:
            compose_data['services'] = {}

        compose_data['services'][service_name] = service_config

        # Backup erstellen
        backup_file = f'{compose_file}.backup'
        with open(backup_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)

        # Aktualisierte docker-compose.yml schreiben
        with open(compose_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Service '{service_name}' erfolgreich zu {compose_file} hinzugefügt")
        print(f"📋 Port: {SERVICE_PORTS.get(service_name, 8000)}")
        print(f"💾 Backup erstellt: {backup_file}")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren von {compose_file}: {str(e)}")
        return False

def main():
    """Hauptfunktion"""

    if len(sys.argv) != 2:
        print("❌ Verwendung: python generate_service_config.py <service_name>")
        print("\n📋 Verfügbare Services:")
        for service in SERVICE_CONFIGS.keys():
            config = SERVICE_CONFIGS[service]
            port = SERVICE_PORTS.get(service, 8000)
            print(f"  {service:<20} (Port {port}) - {config['description']}")
        sys.exit(1)

    service_name = sys.argv[1]

    print(f"🔧 Generiere Service-Konfiguration für: {service_name}")

    # Service-Verzeichnis prüfen
    service_dir = f'services/{service_name}'
    if not os.path.exists(service_dir):
        print(f"❌ Service-Verzeichnis {service_dir} nicht gefunden")
        sys.exit(1)

    # Dockerfile.cpu prüfen
    dockerfile_cpu = f'{service_dir}/Dockerfile.cpu'
    if not os.path.exists(dockerfile_cpu):
        print(f"⚠️ {dockerfile_cpu} nicht gefunden - wird automatisch erstellt")

    # Service zu docker-compose.yml hinzufügen
    if update_docker_compose(service_name):
        print(f"🎉 Service '{service_name}' erfolgreich integriert!")
        print(f"\n📊 Nächste Schritte:")
        print(f"  1. docker-compose build {service_name}")
        print(f"  2. docker-compose up -d {service_name}")
        print(f"  3. make service-test SERVICE={service_name}")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
