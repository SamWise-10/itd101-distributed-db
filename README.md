# Distributed Database CRUD API
### ITD101 - Distributed Database Systems | Capstone Demo Project

A single FastAPI REST API that writes to and reads from **5 cloud databases simultaneously** — demonstrating distributed database architecture through a practical, hands-on demo.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│                  http://localhost:8000/docs                      │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP Request
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│                    (app/routes/items.py)                         │
│                                                                  │
│   POST /items  ──────────── asyncio.gather() ────────────────   │
│   PUT  /items/{id}                   │                           │
│   DELETE /items/{id}                 │                           │
└──────────────────────────────────────┼──────────────────────────┘
                                       │ simultaneous writes
           ┌───────────┬───────────┬───┴───────┬───────────┐
           ▼           ▼           ▼           ▼           ▼
    ┌────────────┐ ┌────────┐ ┌─────────┐ ┌───────┐ ┌──────────┐
    │ PostgreSQL │ │ MySQL  │ │ MongoDB │ │ Redis │ │Cassandra │
    │  (RDBMS 1) │ │(RDBMS2)│ │(NoSQL 1)│ │(NoSQL2│ │(NoSQL 3) │
    │    Neon    │ │Railway │ │  Atlas  │ │ Redis │ │DataStax  │
    │            │ │        │ │         │ │ Cloud │ │  Astra   │
    └────────────┘ └────────┘ └─────────┘ └───────┘ └──────────┘
```

**GET requests** read from PostgreSQL (primary). **Write/Update/Delete** fan out to all 5.

> All 5 databases are hosted in the cloud — no local database containers needed.

---

## What Is a Distributed Database? (ELI5 for Students)

Imagine you have a very important document — like your class schedule. If you only write it down in one notebook and you lose that notebook, the schedule is gone forever. But if you write it in 5 different notebooks and keep them in 5 different places, you'd have to lose ALL 5 before the schedule is truly lost.

A **distributed database** works the same way. Instead of storing your data in one place (one server), it stores copies in multiple places at the same time. When you save something, it gets written to multiple databases — maybe some in the same building, some in different cities. This way, if one database crashes, the others keep running. No data loss, no downtime.

This is why big apps like Facebook, Netflix, and Grab use distributed databases. Netflix has millions of users streaming simultaneously — one database could never handle that load. By distributing the data across hundreds of machines, they can serve millions of requests per second. If one machine dies at 2am, the system automatically switches to another — users don't even notice.

Our project is a simplified, educational version of this concept. We use 5 different cloud databases (a mix of relational and NoSQL) to show that data can live in multiple places simultaneously. The key insight is: **one write request → data exists in many places → system is fault-tolerant and scalable**.

---

## Database Choices & Why

| Database | Type | Cloud Service | Why We Chose It |
|---|---|---|---|
| **PostgreSQL** | RDBMS | [Neon](https://neon.tech) | Industry standard, best async Python driver (`asyncpg`), free tier with no credit card |
| **MySQL** | RDBMS | [Railway](https://railway.app) | Most recognized name in web dev, common in LAMP stack |
| **MongoDB** | Document (NoSQL) | [MongoDB Atlas](https://www.mongodb.com/atlas) | Most popular NoSQL, stores JSON docs naturally, great for beginners |
| **Redis** | Key-Value (NoSQL) | [Redis Cloud](https://redis.com/try-free/) | Blazing fast in-memory store, great for caching concepts, 30MB free |
| **Cassandra** | Wide-Column (NoSQL) | [DataStax Astra](https://astra.datastax.com) | Built for distributed systems, used by Netflix/Instagram, 80GB free via Data API |

---

## Prerequisites

Make sure these are installed before you start:

| Tool | Version | Download |
|---|---|---|
| Docker Desktop | Latest | https://www.docker.com/products/docker-desktop/ |
| VS Code | Latest | https://code.visualstudio.com/ |
| Git | Any | https://git-scm.com/ |

> **Note:** You do NOT need Python installed locally. Python runs inside Docker.

---

## Setup Instructions

### Step 1: Clone the project
```bash
git clone <your-repo-url>
cd distributed-crud-api
```

### Step 2: Create your `.env` file

Copy the template below into a file named `.env` in the project root and fill in your own cloud credentials:

```env
# PostgreSQL — Neon (neon.tech)
POSTGRES_URL=postgresql://<user>:<password>@<host>/neondb?sslmode=require

# MySQL — Railway (railway.app)
MYSQL_HOST=<your-railway-proxy-host>
MYSQL_PORT=<port>
MYSQL_USER=root
MYSQL_PASSWORD=<your-railway-password>
MYSQL_DB=railway

# MongoDB — Atlas (mongodb.com/atlas)
MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
MONGO_DB=distributed_db

# Redis — Redis Cloud (redis.com/try-free)
REDIS_HOST=<your-redis-cloud-host>
REDIS_PORT=<port>
REDIS_PASSWORD=<your-redis-password>

# Cassandra — DataStax Astra (astra.datastax.com)
ASTRA_API_ENDPOINT=https://<database-id>-<region>.apps.astra.datastax.com
ASTRA_TOKEN=AstraCS:<your-token>
```

> **Important:** Never commit your `.env` file to GitHub. It's listed in `.gitignore`.

### Step 3: Check that Docker Desktop is running
Open Docker Desktop and make sure you see the green "Engine running" status.

### Step 4: Start the API

> Make sure your terminal is inside the `distributed-crud-api` folder, not the parent folder.

```bash
cd "distributed-crud-api"
docker-compose up --build
```

Docker will build the FastAPI image and start the container. All 5 databases connect to their cloud services on startup.

### Step 5: Wait for startup

You'll know everything is ready when you see:
```
dist_api  | ✅ PostgreSQL connected and table ready
dist_api  | ✅ MySQL connected and table ready
dist_api  | ✅ MongoDB connected and collection ready
dist_api  | ✅ Redis connected
dist_api  | ✅ Cassandra (DataStax Astra) connected
dist_api  | INFO:     Application startup complete.
```

### Step 6: Open Swagger UI
Visit: **http://localhost:8000/docs**

---

## How to Test the API

### Using Swagger UI (Recommended for Demo)

1. Open http://localhost:8000/docs
2. Click on **`POST /items`** → **"Try it out"**
3. Edit the request body and click **"Execute"**
4. Copy the `id` from the response
5. Use **`GET /items/{id}/verify`** with that ID — it reads from ALL 5 databases and shows results side by side!

### Endpoint Reference

| Method | Endpoint | What it does |
|---|---|---|
| `POST` | `/items` | Create item in ALL 5 databases |
| `GET` | `/items` | List all items (reads from PostgreSQL) |
| `GET` | `/items/{id}` | Get one item by ID (PostgreSQL) |
| `PUT` | `/items/{id}` | Update item in ALL 5 databases |
| `DELETE` | `/items/{id}` | Delete item from ALL 5 databases |
| `GET` | `/items/{id}/verify` | **DEMO:** Read from all 5 and compare! |
| `GET` | `/health` | Check API health |

### Using curl (Command Line)
```bash
# Create an item
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "A fast laptop", "price": 999.99, "quantity": 5}'

# Get all items
curl http://localhost:8000/items

# Get one item (replace with real ID)
curl http://localhost:8000/items/YOUR-UUID-HERE

# Verify in all databases
curl http://localhost:8000/items/YOUR-UUID-HERE/verify
```

---

## Project Structure

```
distributed-crud-api/
│
├── docker-compose.yml     ← Starts the API container (DBs are all in the cloud)
├── Dockerfile             ← Builds the FastAPI app into a container
├── requirements.txt       ← Python package dependencies
├── .env                   ← Your cloud DB credentials (DO NOT commit to GitHub)
│
├── app/
│   ├── main.py            ← App entry point, startup/shutdown hooks
│   ├── models.py          ← Pydantic data models (Item shape)
│   ├── config.py          ← Loads .env variables
│   │
│   ├── databases/         ← One file per database: manages connection
│   │   ├── postgres_db.py
│   │   ├── mysql_db.py
│   │   ├── mongo_db.py
│   │   ├── redis_db.py
│   │   └── cassandra_db.py
│   │
│   ├── crud/              ← One file per database: Create/Read/Update/Delete
│   │   ├── postgres_crud.py
│   │   ├── mysql_crud.py
│   │   ├── mongo_crud.py
│   │   ├── redis_crud.py
│   │   └── cassandra_crud.py
│   │
│   └── routes/
│       └── items.py       ← The actual API endpoints (this is the main show!)
```

---

## How the "Fan-Out" Works (Technical Explanation)

The key piece of code in `app/routes/items.py` is the `fan_out_write()` helper:

```python
results = await asyncio.gather(*coroutines, return_exceptions=True)
```

`asyncio.gather()` is Python's way of running multiple async operations **at the same time** (concurrently). Instead of:
- Write to PostgreSQL... wait 10ms...
- Write to MySQL... wait 10ms...
- Write to MongoDB... wait 10ms...
- *(total: ~50ms)*

We do:
- Write to ALL 5 **at the same time**... wait ~10ms...
- *(total: ~10ms)*

The `return_exceptions=True` parameter means if one database throws an error, `gather()` doesn't cancel the others — it just records the exception as a result. This gives us **basic fault tolerance**: one failure doesn't crash the whole request.

---

## Common Errors & Fixes

### ❌ A database shows up in `databases_failed`
The API is still fault-tolerant — the other databases succeeded. Check your `.env` credentials for that database and restart:
```bash
docker-compose down && docker-compose up --build
```

### ❌ MySQL connection failed (SSL error)
Railway's public proxy requires SSL. The `mysql_db.py` already handles this with a custom SSL context — make sure you're using the **public proxy hostname** (e.g. `yamanote.proxy.rlwy.net`) not the internal hostname.

### ❌ motor / pymongo ImportError
```
cannot import name '_QUERY_OPTIONS' from 'pymongo.cursor'
```
This happens if pymongo gets upgraded to 4.9+. The fix is already applied — `requirements.txt` pins `pymongo==4.8.0`. Rebuild the image:
```bash
docker-compose down && docker-compose up --build
```

### ❌ Changes to Python code not reflecting
```bash
docker-compose restart api
# OR rebuild completely:
docker-compose up --build
```

---

## Useful Docker Commands

> All commands must be run from inside the `distributed-crud-api` folder.

```bash
# Start and build
docker-compose up --build

# Start in background
docker-compose up -d --build

# View live logs
docker-compose logs -f

# View API logs only
docker-compose logs -f api

# Stop the container
docker-compose down

# Rebuild from scratch
docker-compose down && docker-compose up --build

# Check running containers
docker ps
```

---

*Built for ITD101 - Distributed Database Systems*
*Stack: FastAPI + PostgreSQL (Neon) + MySQL (Railway) + MongoDB (Atlas) + Redis Cloud + Cassandra (DataStax Astra) + Docker*
