import aiomysql
from datetime import datetime
from typing import Optional
from app.databases.mysql_db import get_connection


async def create_item(item_id: str, name: str, description: str,
                      price: float, quantity: int, created_at: datetime) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("MySQL is not connected")
    async with connection.cursor() as cursor:
        await cursor.execute("""
            INSERT INTO items (id, name, description, price, quantity, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (item_id, name, description, price, quantity, created_at, created_at))
    return True


async def get_item(item_id: str) -> Optional[dict]:
    connection = get_connection()
    if not connection:
        raise Exception("MySQL is not connected")
    async with connection.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        return await cursor.fetchone()


async def get_all_items() -> list[dict]:
    connection = get_connection()
    if not connection:
        raise Exception("MySQL is not connected")
    async with connection.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        return list(await cursor.fetchall())


async def update_item(item_id: str, name: Optional[str], description: Optional[str],
                      price: Optional[float], quantity: Optional[int],
                      updated_at: datetime) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("MySQL is not connected")
    set_parts = []
    values = []
    if name is not None:
        set_parts.append("name = %s"); values.append(name)
    if description is not None:
        set_parts.append("description = %s"); values.append(description)
    if price is not None:
        set_parts.append("price = %s"); values.append(price)
    if quantity is not None:
        set_parts.append("quantity = %s"); values.append(quantity)
    set_parts.append("updated_at = %s"); values.append(updated_at)
    values.append(item_id)
    async with connection.cursor() as cursor:
        await cursor.execute(f"UPDATE items SET {', '.join(set_parts)} WHERE id = %s", tuple(values))
        return cursor.rowcount > 0


async def delete_item(item_id: str) -> bool:
    connection = get_connection()
    if not connection:
        raise Exception("MySQL is not connected")
    async with connection.cursor() as cursor:
        await cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        return cursor.rowcount > 0
