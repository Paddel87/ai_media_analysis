import redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RedisConfig:
    def __init__(self, host: str = 'redis', port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._client: Optional[redis.Redis] = None
        
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                max_connections=100
            )
        return self._client
        
    def configure_redis(self):
        """Konfiguriert Redis für optimale Performance"""
        try:
            # Memory Management
            self.client.config_set('maxmemory', '2gb')
            self.client.config_set('maxmemory-policy', 'allkeys-lru')
            
            # Persistence
            self.client.config_set('save', '900 1 300 10 60 10000')
            self.client.config_set('appendonly', 'yes')
            self.client.config_set('appendfsync', 'everysec')
            
            # Performance
            self.client.config_set('tcp-keepalive', '300')
            self.client.config_set('timeout', '0')
            self.client.config_set('tcp-backlog', '511')
            
            # Logging
            self.client.config_set('loglevel', 'notice')
            
            logger.info("Redis erfolgreich konfiguriert")
            
        except Exception as e:
            logger.error(f"Fehler bei der Redis-Konfiguration: {str(e)}")
            raise
            
    def get_redis_stats(self) -> dict:
        """Gibt Redis-Statistiken zurück"""
        try:
            info = self.client.info()
            return {
                'used_memory': info['used_memory_human'],
                'connected_clients': info['connected_clients'],
                'total_connections_received': info['total_connections_received'],
                'total_commands_processed': info['total_commands_processed'],
                'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec'],
                'hit_rate': info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Redis-Statistiken: {str(e)}")
            return {} 