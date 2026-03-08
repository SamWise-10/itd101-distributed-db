from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.databases import postgres_db, mysql_db, mongo_db, redis_db, cassandra_db
from app.routes import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print("🚀 Starting Distributed Database API...")
    print("="*60)

    await postgres_db.connect()
    await mysql_db.connect()
    await mongo_db.connect()
    await redis_db.connect()
    await cassandra_db.connect()

    print("="*60)
    print("✅ Startup complete! API is ready.")
    print("📖 Swagger UI: http://localhost:8000/docs")
    print("="*60 + "\n")

    yield

    print("\n🛑 Shutting down...")
    await postgres_db.disconnect()
    await mysql_db.disconnect()
    await mongo_db.disconnect()
    await redis_db.disconnect()
    await cassandra_db.disconnect()


app = FastAPI(
    title="Distributed Database CRUD API",
    description="""
## ITD101 - Distributed Database Systems Demo

Single REST API that writes to and reads from **5 cloud databases simultaneously**.

| Type | Database | Cloud |
|------|----------|-------|
| RDBMS #1 | **PostgreSQL** | Neon |
| RDBMS #2 | **MySQL** | Railway |
| NoSQL #1 | **MongoDB** | Atlas |
| NoSQL #2 | **Redis** | Redis Cloud |
| NoSQL #3 | **Cassandra** | DataStax Astra |

- **POST /items** → Creates item in ALL 5 databases
- **GET /items** → Reads from PostgreSQL (primary)
- **PUT /items/{id}** → Updates ALL 5 databases
- **DELETE /items/{id}** → Deletes from ALL 5 databases
- **GET /items/{id}/verify** → Reads from ALL 5 and compares (best demo!)
    """,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(items.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Distributed Database API is running!",
        "docs": "Visit /docs for Swagger UI",
        "databases": ["PostgreSQL (Neon)", "MySQL (Railway)", "MongoDB (Atlas)",
                      "Redis Cloud", "Cassandra (DataStax Astra)"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
