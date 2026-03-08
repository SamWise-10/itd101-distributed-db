import ssl
import aiomysql
from app.config import settings

mysql_connection = None


async def connect():
    global mysql_connection
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        mysql_connection = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            autocommit=True,
            ssl=ssl_ctx
        )
        async with mysql_connection.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id          VARCHAR(36)  PRIMARY KEY,
                    name        VARCHAR(255) NOT NULL,
                    description TEXT         NOT NULL,
                    price       DOUBLE       NOT NULL,
                    quantity    INT          NOT NULL,
                    created_at  DATETIME     NOT NULL,
                    updated_at  DATETIME     NOT NULL
                )
            """)
        print("✅ MySQL connected and table ready")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        mysql_connection = None


async def disconnect():
    global mysql_connection
    if mysql_connection:
        mysql_connection.close()
        print("🔌 MySQL disconnected")


def get_connection():
    return mysql_connection
