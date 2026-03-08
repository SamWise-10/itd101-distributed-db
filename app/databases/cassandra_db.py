from astrapy import DataAPIClient
from app.config import settings

astra_collection = None


def _blocking_connect():
    client = DataAPIClient(token=settings.ASTRA_TOKEN)
    db = client.get_database_by_api_endpoint(settings.ASTRA_API_ENDPOINT)
    try:
        db.create_collection("items")
    except Exception:
        pass
    return db.get_collection("items")


async def connect():
    global astra_collection
    import asyncio
    try:
        astra_collection = await asyncio.to_thread(_blocking_connect)
        print("✅ Cassandra (DataStax Astra) connected")
    except Exception as e:
        print(f"❌ Cassandra (Astra) connection failed: {e}")
        astra_collection = None


async def disconnect():
    global astra_collection
    astra_collection = None
    print("🔌 Cassandra (Astra) disconnected")


def get_collection():
    return astra_collection
