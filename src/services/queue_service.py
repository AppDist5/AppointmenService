import json
from datetime import datetime
from src.config.redis import get_redis_client, is_redis_connected

class QueueService:
    AUDIT_CHANNEL = 'audit-events'
    
    def __init__(self):
        self.redis_available = is_redis_connected()
        if self.redis_available:
            print('✅ QueueService using Redis (Upstash)')
        else:
            print('⚠️ QueueService: Redis not available')
    
    def publish(self, routing_key, data):
        client = get_redis_client()
        
        if client is None:
            print('⚠️ Queue not available, skipping event publishing')
            self.redis_available = False
            return
        
        try:
            message = json.dumps({
                'service': 'appointment-service',
                'action': routing_key,
                'entityType': 'appointment',
                'entityId': str(data.get('id', '')),
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            client.publish(self.AUDIT_CHANNEL, message)
            
            print(f'📤 Event published to Redis: {routing_key}', {
                'channel': self.AUDIT_CHANNEL,
                'entityId': data.get('id'),
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f'❌ Error publishing to Redis: {e}')
            self.redis_available = False