import json
from datetime import datetime
from typing import Optional
from app.databases.redis_db import get_client


def _key(item_id: str) -> str:
    return f"item:{item_id}"


def _serialize(item_id: str, name: str, description: str,
               price: float, quantity: int,
               created_at: datetime, updated_at: datetime) -> str:
    return json.dumps({
        "id": item_id,
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat()
    })


def _deserialize(json_string: str) -> dict:
    data = json.loads(json_string)
    data["created_at"] = datetime.fromisoformat(data["created_at"])
    data["updated_at"] = datetime.fromisoformat(data["updated_at"])
    return data


async def create_item(item_id: str, name: str, description: str,
                      price: float, quantity: int, created_at: datetime) -> bool:
    client = get_client()
    if not client:
        raise Exception("Redis is not connected")
    await client.set(_key(item_id), _serialize(item_id, name, description, price, quantity, created_at, created_at))
    await client.sadd("item_ids", item_id)
    return True


async def get_item(item_id: str) -> Optional[dict]:
    client = get_client()
    if not client:
        raise Exception("Redis is not connected")
    data = await client.get(_key(item_id))
    return _deserialize(data) if data else None


async def get_all_items() -> list[dict]:
    client = get_client()
    if not client:
        raise Exception("Redis is not connected")
    all_ids = await client.smembers("item_ids")
    if not all_ids:
        return []
    items = []
    for item_id in all_ids:
        data = await client.get(_key(item_id))
        if data:
            items.append(_deserialize(data))
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items


async def update_item(item_id: str, name: Optional[str], description: Optional[str],
                      price: Optional[float], quantity: Optional[int],
                      updated_at: datetime) -> bool:
    client = get_client()
    if not client:
        raise Exception("Redis is not connected")
    data = await client.get(_key(item_id))
    if not data:
        return False
    existing = _deserialize(data)
    if name is not None:
        existing["name"] = name
    if description is not None:
        existing["description"] = description
    if price is not None:
        existing["price"] = price
    if quantity is not None:
        existing["quantity"] = quantity
    existing["updated_at"] = updated_at
    new_json = json.dumps({**existing, "created_at": existing["created_at"].isoformat(), "updated_at": existing["updated_at"].isoformat()})
    await client.set(_key(item_id), new_json)
    return True


async def delete_item(item_id: str) -> bool:
    client = get_client()
    if not client:
        raise Exception("Redis is not connected")
    deleted = await client.delete(_key(item_id))
    await client.srem("item_ids", item_id)
    return deleted > 0
