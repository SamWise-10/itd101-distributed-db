import redis.asyncio as aioredis
from app.config import settings

redis_client = None


async def connect():
    global redis_client
    try:
        redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        await redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        redis_client = None


async def disconnect():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        print("🔌 Redis disconnected")


def get_client():
    return redis_client
