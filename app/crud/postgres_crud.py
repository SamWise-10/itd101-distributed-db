from datetime import datetime
from typing import Optional
from app.databases.postgres_db import get_connection


async def create_item(item_id: str, name: str, description: str,
                      price: float, quantity: int, created_at: datetime) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("PostgreSQL is not connected")
    await connection.execute("""
        INSERT INTO items (id, name, description, price, quantity, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $6)
    """, item_id, name, description, price, quantity, created_at)
    return True


async def get_item(item_id: str) -> Optional[dict]:
    connection = get_connection()
    if not connection:
        raise Exception("PostgreSQL is not connected")
    row = await connection.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
    return dict(row) if row else None


async def get_all_items() -> list[dict]:
    connection = get_connection()
    if not connection:
        raise Exception("PostgreSQL is not connected")
    rows = await connection.fetch("SELECT * FROM items ORDER BY created_at DESC")
    return [dict(row) for row in rows]


async def update_item(item_id: str, name: Optional[str], description: Optional[str],
                      price: Optional[float], quantity: Optional[int],
                      updated_at: datetime) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("PostgreSQL is not connected")
    set_parts = []
    values = []
    index = 1
    if name is not None:
        set_parts.append(f"name = ${index}"); values.append(name); index += 1
    if description is not None:
        set_parts.append(f"description = ${index}"); values.append(description); index += 1
    if price is not None:
        set_parts.append(f"price = ${index}"); values.append(price); index += 1
    if quantity is not None:
        set_parts.append(f"quantity = ${index}"); values.append(quantity); index += 1
    set_parts.append(f"updated_at = ${index}"); values.append(updated_at); index += 1
    values.append(item_id)
    result = await connection.execute(f"UPDATE items SET {', '.join(set_parts)} WHERE id = ${index}", *values)
    return result == "UPDATE 1"


async def delete_item(item_id: str) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("PostgreSQL is not connected")
    result = await connection.execute("DELETE FROM items WHERE id = $1", item_id)
    return result == "DELETE 1"
