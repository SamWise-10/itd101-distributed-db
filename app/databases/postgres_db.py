import asyncpg
from app.config import settings

postgres_connection = None


async def connect():
    global postgres_connection
    try:
        postgres_connection = await asyncpg.connect(settings.POSTGRES_URL)
        await postgres_connection.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id          VARCHAR(36)      PRIMARY KEY,
                name        VARCHAR(255)     NOT NULL,
                description TEXT             NOT NULL DEFAULT '',
                price       DOUBLE PRECISION NOT NULL,
                quantity    INTEGER          NOT NULL,
                created_at  TIMESTAMP        NOT NULL,
                updated_at  TIMESTAMP        NOT NULL
            )
        """)
        print("✅ PostgreSQL connected and table ready")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        postgres_connection = None


async def disconnect():
    global postgres_connection
    if postgres_connection:
        await postgres_connection.close()
        print("🔌 PostgreSQL disconnected")


def get_connection():
    return postgres_connection
