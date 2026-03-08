from datetime import datetime
from typing import Optional
from app.databases.mongo_db import get_collection


async def create_item(item_id: str, name: str, description: str,
                      price: float, quantity: int, created_at: datetime) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("MongoDB is not connected")
    await collection.insert_one({
        "id": item_id, "name": name, "description": description,
        "price": price, "quantity": quantity,
        "created_at": created_at, "updated_at": created_at
    })
    return True


async def get_item(item_id: str) -> Optional[dict]:
    collection = get_collection()
    if collection is None:
        raise Exception("MongoDB is not connected")
    document = await collection.find_one({"id": item_id})
    if document is None:
        return None
    document.pop("_id", None)
    return document


async def get_all_items() -> list[dict]:
    collection = get_collection()
    if collection is None:
        raise Exception("MongoDB is not connected")
    documents = await collection.find({}).sort("created_at", -1).to_list(length=None)
    for doc in documents:
        doc.pop("_id", None)
    return documents


async def update_item(item_id: str, name: Optional[str], description: Optional[str],
                      price: Optional[float], quantity: Optional[int],
                      updated_at: datetime) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("MongoDB is not connected")
    update_fields = {"updated_at": updated_at}
    if name is not None:
        update_fields["name"] = name
    if description is not None:
        update_fields["description"] = description
    if price is not None:
        update_fields["price"] = price
    if quantity is not None:
        update_fields["quantity"] = quantity
    result = await collection.update_one({"id": item_id}, {"$set": update_fields})
    return result.matched_count > 0


async def delete_item(item_id: str) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("MongoDB is not connected")
    result = await collection.delete_one({"id": item_id})
    return result.deleted_count > 0
