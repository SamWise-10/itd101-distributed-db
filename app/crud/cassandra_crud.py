from datetime import datetime
from typing import Optional
from app.databases.cassandra_db import get_collection


def _to_doc(item_id: str, name: str, description: str,
            price: float, quantity: int,
            created_at: datetime, updated_at: datetime) -> dict:
    return {
        "_id": item_id,
        "id": item_id,
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat()
    }


def _from_doc(doc: dict) -> dict:
    doc = dict(doc)
    doc["created_at"] = datetime.fromisoformat(doc["created_at"])
    doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
    return doc


def create_item(item_id: str, name: str, description: str,
                price: float, quantity: int, created_at: datetime) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("Cassandra (Astra) is not connected")
    collection.insert_one(_to_doc(item_id, name, description, price, quantity, created_at, created_at))
    return True


def get_item(item_id: str) -> Optional[dict]:
    collection = get_collection()
    if collection is None:
        raise Exception("Cassandra (Astra) is not connected")
    doc = collection.find_one({"_id": item_id})
    return _from_doc(doc) if doc else None


def get_all_items() -> list[dict]:
    collection = get_collection()
    if collection is None:
        raise Exception("Cassandra (Astra) is not connected")
    docs = list(collection.find({}))
    items = [_from_doc(d) for d in docs]
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items


def update_item(item_id: str, name: Optional[str], description: Optional[str],
                price: Optional[float], quantity: Optional[int],
                updated_at: datetime) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("Cassandra (Astra) is not connected")
    update_fields = {"updated_at": updated_at.isoformat()}
    if name is not None:
        update_fields["name"] = name
    if description is not None:
        update_fields["description"] = description
    if price is not None:
        update_fields["price"] = price
    if quantity is not None:
        update_fields["quantity"] = quantity
    collection.update_one({"_id": item_id}, {"$set": update_fields})
    return True


def delete_item(item_id: str) -> bool:
    collection = get_collection()
    if collection is None:
        raise Exception("Cassandra (Astra) is not connected")
    result = collection.delete_one({"_id": item_id})
    return result.deleted_count > 0
