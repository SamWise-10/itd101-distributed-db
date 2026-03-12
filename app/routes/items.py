import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from app.models import ItemCreate, ItemUpdate, ItemResponse, DistributedResponse
from app.crud import postgres_crud, mysql_crud, mongo_crud, redis_crud, cassandra_crud

router = APIRouter(prefix="/items", tags=["Items"])


class DBTarget(str, Enum):
    all        = "All Databases"
    postgresql = "PostgreSQL"
    mysql      = "MySQL"
    mongodb    = "MongoDB"
    redis      = "Redis"
    cassandra  = "Cassandra"


def resolve_operations(all_ops: dict, target: DBTarget) -> dict:
    if target == DBTarget.all:
        return all_ops
    return {k: v for k, v in all_ops.items() if k == target.value}


async def fan_out_write(operations: dict) -> tuple[list[str], list[str]]:
    db_names = list(operations.keys())
    results = await asyncio.gather(*operations.values(), return_exceptions=True)
    succeeded, failed = [], []
    for db_name, result in zip(db_names, results):
        if isinstance(result, Exception):
            print(f"❌ {db_name} failed: {result}")
            failed.append(db_name)
        else:
            print(f"✅ Saved to {db_name}")
            succeeded.append(db_name)
    return succeeded, failed


@router.post(
    "/",
    response_model=DistributedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create item — choose target database",
    description="Creates the item in the selected database(s). Choose **All Databases** to fan out to all 5 at once."
)
async def create_item(
    item: ItemCreate,
    target: DBTarget = Query(default=DBTarget.all, description="Which database(s) to write to")
):
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n📝 Creating '{item.name}' — target: {target.value}")

    all_operations = {
        "PostgreSQL": postgres_crud.create_item(item_id, item.name, item.description, item.price, item.quantity, now),
        "MySQL":      mysql_crud.create_item(item_id, item.name, item.description, item.price, item.quantity, now),
        "MongoDB":    mongo_crud.create_item(item_id, item.name, item.description, item.price, item.quantity, now),
        "Redis":      redis_crud.create_item(item_id, item.name, item.description, item.price, item.quantity, now),
        "Cassandra":  asyncio.to_thread(cassandra_crud.create_item, item_id, item.name, item.description, item.price, item.quantity, now),
    }
    operations = resolve_operations(all_operations, target)
    succeeded, failed = await fan_out_write(operations)

    if not succeeded:
        raise HTTPException(status_code=500, detail="All selected databases failed. Check logs and verify .env credentials.")

    return DistributedResponse(
        item=ItemResponse(id=item_id, name=item.name, description=item.description,
                          price=item.price, quantity=item.quantity, created_at=now, updated_at=now),
        databases_written=succeeded,
        databases_failed=failed,
        message=f"Item created in {len(succeeded)}/{len(operations)} database(s)."
    )


@router.get(
    "/",
    response_model=List[ItemResponse],
    summary="List all items — choose source database",
    description="Returns all items from the selected database. Defaults to **All Databases** — reads from PostgreSQL and shows results from the first successful source."
)
async def get_all_items(
    target: DBTarget = Query(default=DBTarget.all, description="Which database to read from")
):
    db_label = target.value
    print(f"\n📋 Fetching all items — target: {db_label}")

    read_map = {
        "PostgreSQL": lambda: postgres_crud.get_all_items(),
        "MySQL":      lambda: mysql_crud.get_all_items(),
        "MongoDB":    lambda: mongo_crud.get_all_items(),
        "Redis":      lambda: redis_crud.get_all_items(),
        "Cassandra":  lambda: asyncio.to_thread(cassandra_crud.get_all_items),
    }

    if target == DBTarget.all:
        sources = list(read_map.keys())
    else:
        sources = [target.value]

    for db_name in sources:
        try:
            rows = await read_map[db_name]()
            print(f"✅ Read {len(rows)} item(s) from {db_name}")
            return rows
        except Exception as e:
            print(f"❌ {db_name} failed: {e}")

    raise HTTPException(status_code=500, detail="All selected databases failed to return items.")


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID — choose source database",
    description="Fetches one item from the selected database. Defaults to **All Databases** — tries each in order until one succeeds."
)
async def get_item(
    item_id: str,
    target: DBTarget = Query(default=DBTarget.all, description="Which database to read from")
):
    print(f"\n🔍 Looking up item {item_id} — target: {target.value}")

    read_map = {
        "PostgreSQL": lambda: postgres_crud.get_item(item_id),
        "MySQL":      lambda: mysql_crud.get_item(item_id),
        "MongoDB":    lambda: mongo_crud.get_item(item_id),
        "Redis":      lambda: redis_crud.get_item(item_id),
        "Cassandra":  lambda: asyncio.to_thread(cassandra_crud.get_item, item_id),
    }

    if target == DBTarget.all:
        sources = list(read_map.keys())
    else:
        sources = [target.value]

    for db_name in sources:
        try:
            item = await read_map[db_name]()
            if item is not None:
                print(f"✅ Found in {db_name}")
                return item
        except Exception as e:
            print(f"❌ {db_name} failed: {e}")

    raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")


@router.put(
    "/{item_id}",
    response_model=DistributedResponse,
    summary="Update item — choose target database",
    description="Updates only the fields you provide. Choose **All Databases** to update all 5 at once."
)
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    target: DBTarget = Query(default=DBTarget.all, description="Which database(s) to update")
):
    print(f"\n✏️  Updating item {item_id} — target: {target.value}")
    try:
        existing = await postgres_crud.get_item(item_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    all_operations = {
        "PostgreSQL": postgres_crud.update_item(item_id, item_update.name, item_update.description, item_update.price, item_update.quantity, now),
        "MySQL":      mysql_crud.update_item(item_id, item_update.name, item_update.description, item_update.price, item_update.quantity, now),
        "MongoDB":    mongo_crud.update_item(item_id, item_update.name, item_update.description, item_update.price, item_update.quantity, now),
        "Redis":      redis_crud.update_item(item_id, item_update.name, item_update.description, item_update.price, item_update.quantity, now),
        "Cassandra":  asyncio.to_thread(cassandra_crud.update_item, item_id, item_update.name, item_update.description, item_update.price, item_update.quantity, now),
    }
    operations = resolve_operations(all_operations, target)
    succeeded, failed = await fan_out_write(operations)

    if not succeeded:
        raise HTTPException(status_code=500, detail="All selected database updates failed.")

    updated = await postgres_crud.get_item(item_id)
    return DistributedResponse(
        item=ItemResponse(**updated),
        databases_written=succeeded,
        databases_failed=failed,
        message=f"Item updated in {len(succeeded)}/{len(operations)} database(s)."
    )


@router.delete(
    "/{item_id}",
    response_model=DistributedResponse,
    summary="Delete item — choose target database",
    description="Choose **All Databases** to delete from all 5 at once, or pick one to delete from a single database."
)
async def delete_item(
    item_id: str,
    target: DBTarget = Query(default=DBTarget.all, description="Which database(s) to delete from")
):
    print(f"\n🗑️  Deleting item {item_id} — target: {target.value}")
    try:
        existing = await postgres_crud.get_item(item_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

    snapshot = ItemResponse(**existing)
    all_operations = {
        "PostgreSQL": postgres_crud.delete_item(item_id),
        "MySQL":      mysql_crud.delete_item(item_id),
        "MongoDB":    mongo_crud.delete_item(item_id),
        "Redis":      redis_crud.delete_item(item_id),
        "Cassandra":  asyncio.to_thread(cassandra_crud.delete_item, item_id),
    }
    operations = resolve_operations(all_operations, target)
    succeeded, failed = await fan_out_write(operations)

    return DistributedResponse(
        item=snapshot,
        databases_written=succeeded,
        databases_failed=failed,
        message=f"Item deleted from {len(succeeded)}/{len(operations)} database(s)."
    )


@router.get(
    "/{item_id}/verify",
    summary="Verify item exists in all 5 databases",
    description="Reads the item from ALL 5 databases and compares results. Best demo endpoint!"
)
async def verify_item_in_all_databases(item_id: str):
    print(f"\n🔬 Verifying item {item_id} across all 5 databases...")
    results = await asyncio.gather(
        postgres_crud.get_item(item_id),
        mysql_crud.get_item(item_id),
        mongo_crud.get_item(item_id),
        redis_crud.get_item(item_id),
        asyncio.to_thread(cassandra_crud.get_item, item_id),
        return_exceptions=True
    )
    db_names = ["PostgreSQL (Neon)", "MySQL (Railway)", "MongoDB (Atlas)", "Redis Cloud", "Cassandra (Astra)"]
    verification = {}
    for db_name, result in zip(db_names, results):
        if isinstance(result, Exception):
            verification[db_name] = {"status": "error", "error": str(result)}
        elif result is None:
            verification[db_name] = {"status": "not_found"}
        else:
            verification[db_name] = {"status": "found", "name": result.get("name"), "price": result.get("price"), "quantity": result.get("quantity")}

    found_count = sum(1 for v in verification.values() if v["status"] == "found")
    return {"item_id": item_id, "databases": verification, "summary": f"Found in {found_count}/5 databases"}
