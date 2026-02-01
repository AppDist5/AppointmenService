import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

class RedisClient:
    _instance = None
    
    def __init__(self):
        self.client = None
        self.connect()
    
    def connect(self):
        try:
            self.client = redis.Redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.client.ping()
            print("✅ Connected to Redis (Upstash)")
            return True
        except Exception as e:
            print(f"❌ Redis connection error: {e}")
            self.client = None
            return False
    
    def is_connected(self):
        if self.client is None:
            return self.connect()
        try:
            self.client.ping()
            return True
        except Exception:
            return self.connect()
    
    def get_client(self):
        if not self.is_connected():
            return None
        return self.client

# Singleton instance
redis_client = RedisClient()

def is_redis_connected():
    return redis_client.is_connected()

def get_redis_client():
    return redis_client.get_client()