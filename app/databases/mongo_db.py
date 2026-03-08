import motor.motor_asyncio
from app.config import settings

mongo_client = None
mongo_collection = None


async def connect():
    global mongo_client, mongo_collection
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
        database = mongo_client[settings.MONGO_DB]
        mongo_collection = database["items"]
        await mongo_collection.create_index("id", unique=True)
        await mongo_client.admin.command("ping")
        print("✅ MongoDB connected and collection ready")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        mongo_client = None
        mongo_collection = None


async def disconnect():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("🔌 MongoDB disconnected")


def get_collection():
    return mongo_collection
