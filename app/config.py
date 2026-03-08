import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/db")

    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "railway")

    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "distributed_db")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    ASTRA_API_ENDPOINT: str = os.getenv("ASTRA_API_ENDPOINT", "")
    ASTRA_TOKEN: str = os.getenv("ASTRA_TOKEN", "")


settings = Settings()
