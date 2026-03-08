from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="")
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Laptop",
                "description": "A powerful laptop for coding",
                "price": 999.99,
                "quantity": 10
            }
        }
    }


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Gaming Laptop",
                "price": 1299.99
            }
        }
    }


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Laptop",
                "description": "A powerful laptop for coding",
                "price": 999.99,
                "quantity": 10,
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-01-01T12:00:00"
            }
        }
    }


class DistributedResponse(BaseModel):
    item: ItemResponse
    databases_written: list[str]
    databases_failed: list[str]
    message: str
