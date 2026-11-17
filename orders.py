"""Обработка заказов на Pydantic v2."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class OrderStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int = Field(gt=0)
    customer_email: EmailStr
    total: Decimal = Field(gt=0, decimal_places=2)
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().lower()
        return value


def parse_order(raw: Any) -> Order:
    """Создаёт Order из словаря или объекта БД (ORM)."""
    if isinstance(raw, dict):
        return Order.model_validate(raw)
    return Order.model_validate(raw, from_attributes=True)


def order_to_dict(order: Order) -> dict[str, Any]:
    return order.model_dump()


def order_to_json(order: Order) -> str:
    return order.model_dump_json()
